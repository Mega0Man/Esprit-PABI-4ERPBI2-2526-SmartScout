import { Injectable } from '@angular/core';
import * as faceapi from 'face-api.js';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FaceRecognitionService {
  private modelsLoaded = false;
  private readonly MODEL_URL = '/assets/models';
  private readonly STORAGE_KEY = 'registered_faces';
  private readonly API_URL = 'http://localhost:8090';

  constructor(private http: HttpClient) { }

  async loadModels(): Promise<void> {
    if (this.modelsLoaded) {
      return;
    }

    try {
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(this.MODEL_URL),
        faceapi.nets.faceLandmark68Net.loadFromUri(this.MODEL_URL),
        faceapi.nets.faceRecognitionNet.loadFromUri(this.MODEL_URL),
        faceapi.nets.faceExpressionNet.loadFromUri(this.MODEL_URL)
      ]);
      this.modelsLoaded = true;
      console.log('Face-api models loaded successfully!');
    } catch (error) {
      console.error('Error loading face-api models:', error);
      throw error;
    }
  }

  async detectFace(video: HTMLVideoElement): Promise<faceapi.WithFaceDescriptor<faceapi.WithFaceLandmarks<{ detection: faceapi.FaceDetection; }, faceapi.FaceLandmarks68>> | null> {
    const detection = await faceapi
      .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceDescriptor();

    return detection || null;
  }

  async detectAllFaces(video: HTMLVideoElement): Promise<faceapi.WithFaceDescriptor<faceapi.WithFaceLandmarks<{ detection: faceapi.FaceDetection; }, faceapi.FaceLandmarks68>>[]> {
    const detections = await faceapi
      .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
      .withFaceLandmarks()
      .withFaceDescriptors();

    return detections;
  }

  async registerFace(username: string, video: HTMLVideoElement): Promise<boolean> {
    console.log('Registering face for username:', username);
    const detection = await this.detectFace(video);
    if (!detection) {
      console.log('No face detected for registration');
      return false;
    }

    // Still save to localStorage for immediate local use if needed, 
    // but the main storage is now the backend database via LoginComponent
    const registeredFaces = this.getRegisteredFaces();
    registeredFaces[username] = Array.from(detection.descriptor);
    this.saveRegisteredFaces(registeredFaces);
    console.log('Face registered successfully! Current registered faces:', Object.keys(registeredFaces));
    return true;
  }

  async recognizeFace(video: HTMLVideoElement, existingDetection?: any): Promise<{ username: string; distance: number } | null> {
    const detection = existingDetection || await this.detectFace(video);
    if (!detection) {
      console.log('No face detected for recognition');
      return null;
    }

    // Try to get descriptors from backend
    let registeredFaces: Record<string, number[]> = {};
    try {
      registeredFaces = await firstValueFrom(this.http.get<Record<string, number[]>>(`${this.API_URL}/face-descriptors`));
    } catch (err) {
      console.error('Failed to fetch face descriptors from backend, falling back to local storage', err);
      registeredFaces = this.getRegisteredFaces();
    }

    const labels = Object.keys(registeredFaces);
    
    if (labels.length === 0) {
      console.log('No registered faces found in database or localStorage');
      return null;
    }

    const labeledDescriptors = labels.map(label => {
      const descriptor = new Float32Array(registeredFaces[label]);
      return new faceapi.LabeledFaceDescriptors(label, [descriptor]);
    });

    // Use a very lenient threshold (0.8) to ensure login happens easily.
    // In face-api.js, a lower distance means a better match. 
    // 0.6 is default. 0.8 is very lenient.
    const faceMatcher = new faceapi.FaceMatcher(labeledDescriptors, 0.8);
    const bestMatch = faceMatcher.findBestMatch(detection.descriptor);
    
    console.log(`Recognition attempt for ${labels.length} users. Best match: ${bestMatch.toString()}`);

    if (bestMatch.label === 'unknown') {
      return null;
    }

    return {
      username: bestMatch.label,
      distance: bestMatch.distance
    };
  }

  private getRegisteredFaces(): Record<string, number[]> {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  }

  private saveRegisteredFaces(faces: Record<string, number[]>): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(faces));
  }

  isUserRegistered(username: string): boolean {
    const registeredFaces = this.getRegisteredFaces();
    return !!registeredFaces[username];
  }

  getRegisteredUsers(): string[] {
    return Object.keys(this.getRegisteredFaces());
  }

  deleteUser(username: string): void {
    const registeredFaces = this.getRegisteredFaces();
    delete registeredFaces[username];
    this.saveRegisteredFaces(registeredFaces);
  }

  drawDetection(canvas: HTMLCanvasElement, video: HTMLVideoElement, detections: any): void {
    const width = video.clientWidth || video.videoWidth;
    const height = video.clientHeight || video.videoHeight;
    
    if (width === 0 || height === 0 || !detections) {
      return;
    }

    const displaySize = { width, height };
    faceapi.matchDimensions(canvas, displaySize);
    const resizedDetections = faceapi.resizeResults(detections, displaySize);
    faceapi.draw.drawDetections(canvas, resizedDetections);
    faceapi.draw.drawFaceLandmarks(canvas, resizedDetections);
  }
}
