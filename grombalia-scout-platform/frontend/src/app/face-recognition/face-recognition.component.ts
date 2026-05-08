import { Component, OnInit, ViewChild, ElementRef, Output, EventEmitter, Input, OnDestroy, OnChanges, SimpleChanges } from '@angular/core';
import { FaceRecognitionService } from '../services/face-recognition.service';

@Component({
  selector: 'app-face-recognition',
  templateUrl: './face-recognition.component.html',
  styleUrls: ['./face-recognition.component.css']
})
export class FaceRecognitionComponent implements OnInit, OnDestroy, OnChanges {
  @ViewChild('video') videoRef!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;

  @Input() mode: 'register' | 'login' = 'login';
  @Input() username?: string;
  @Input() disabled: boolean = false;
  @Output() faceDetected = new EventEmitter<any>();
  @Output() faceRecognized = new EventEmitter<string>();
  @Output() faceRegistered = new EventEmitter<boolean>();
  @Output() error = new EventEmitter<string>();

  isLoading = true;
  isCameraActive = false;
  detectionInterval: any;
  stream: MediaStream | null = null;
  faceDetectedState = false;
  guideMessage = 'Position your face in the frame';
  private isProcessing = false;

  constructor(private faceService: FaceRecognitionService) { }

  async ngOnInit(): Promise<void> {
    try {
      await this.faceService.loadModels();
      this.isLoading = false;
      await this.startCamera();
    } catch (err) {
      this.error.emit('Failed to load face recognition models');
      console.error(err);
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if ((changes['mode'] || changes['username']) && this.isCameraActive) {
      this.restartDetection();
    }
  }

  ngOnDestroy(): void {
    this.isCameraActive = false;
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
    }
    this.stopCamera();
  }

  restartDetection(): void {
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
    }
    if (this.isCameraActive) {
      this.startDetection();
    }
  }

  async startCamera(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      if (this.videoRef && this.videoRef.nativeElement) {
        const video = this.videoRef.nativeElement;
        video.srcObject = this.stream;
        
        // Use a promise to track play state
        video.onloadedmetadata = async () => {
          try {
            if (this.stream) { // Check if we haven't stopped in the meantime
              await video.play();
              this.isCameraActive = true;
              this.startDetection();
            }
          } catch (err: any) {
            if (err.name !== 'AbortError') {
              console.error('Error playing video:', err);
            }
          }
        };
      }
    } catch (err) {
      this.error.emit('Failed to access camera. Please ensure you have given permission.');
      console.error(err);
    }
  }

  stopCamera(): void {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.videoRef && this.videoRef.nativeElement) {
      this.videoRef.nativeElement.srcObject = null;
    }
    this.isCameraActive = false;
  }

  startDetection(): void {
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
    }

    this.detectionInterval = setInterval(async () => {
      if (!this.videoRef || !this.canvasRef || !this.isCameraActive || this.isProcessing) {
        return;
      }

      this.isProcessing = true;

      try {
        const video = this.videoRef.nativeElement;
        const canvas = this.canvasRef.nativeElement;

        // Skip if video is not ready
        if (video.readyState !== 4 || video.videoWidth === 0) {
          this.isProcessing = false;
          return;
        }

        const detection = await this.faceService.detectFace(video);
        
        if (detection) {
          const { x, y, width, height } = detection.detection.box;
          const isPositioned = this.checkFacePosition(x, y, width, height);
          
          this.faceDetectedState = isPositioned;
          if (isPositioned) {
            this.faceService.drawDetection(canvas, video, detection);
            this.faceDetected.emit(detection);

            if (this.mode === 'login') {
               this.guideMessage = 'Scanning...';
               const result = await this.faceService.recognizeFace(video, detection);
               if (result) {
                 console.log('Login success for:', result.username);
                 this.guideMessage = `Welcome, ${result.username}!`;
                 clearInterval(this.detectionInterval);
                 this.detectionInterval = null;
                 
                 // Emit immediately, stop camera after a short delay so user sees message
                 this.faceRecognized.emit(result.username);
                 
                 setTimeout(() => {
                   this.stopCamera();
                 }, 2000);
               } else {
                   // Optional: Check if the face is actually registered but just not recognized
                   // For now, keep the generic message to avoid leaking user info if someone else tries
                   this.guideMessage = 'Face not recognized. Keep looking...';
                 }
               } else {
                 this.guideMessage = 'Face detected! Ready to register.';
               }
           } else {
             this.faceService.drawDetection(canvas, video, detection);
             // guideMessage is updated inside checkFacePosition
           }
         } else {
           this.faceDetectedState = false;
           this.guideMessage = 'Position your face in the frame';
           const ctx = canvas.getContext('2d');
           if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
         }
       } catch (err) {
         console.error('Detection error:', err);
       } finally {
         this.isProcessing = false;
       }
     }, 300);
   }

  private checkFacePosition(x: number, y: number, width: number, height: number): boolean {
    const video = this.videoRef.nativeElement;
    const vWidth = video.videoWidth || 640;
    const vHeight = video.videoHeight || 480;

    const centerX = x + width / 2;
    const centerY = y + height / 2;
    
    // Calculate boundaries based on actual video size
    const minX = vWidth * 0.28; // ~180 for 640
    const maxX = vWidth * 0.72; // ~460 for 640
    const minY = vHeight * 0.16; // ~80 for 480
    const maxY = vHeight * 0.83; // ~400 for 480
    
    const isCentered = centerX > minX && centerX < maxX && centerY > minY && centerY < maxY;
    const isRightSize = width > (vWidth * 0.18) && width < (vWidth * 0.78);

    if (!isCentered) {
      if (centerX < minX) this.guideMessage = 'Move slightly right';
      else if (centerX > maxX) this.guideMessage = 'Move slightly left';
      else if (centerY < minY) this.guideMessage = 'Move slightly down';
      else if (centerY > maxY) this.guideMessage = 'Move slightly up';
      else this.guideMessage = 'Center your face';
      return false;
    }
    
    if (!isRightSize) {
      this.guideMessage = width <= (vWidth * 0.18) ? 'Move closer' : 'Move further back';
      return false;
    }

    return true;
  }

  async registerFace(): Promise<void> {
    if (!this.username || !this.videoRef) {
      this.error.emit('Username is required');
      return;
    }

    try {
      const success = await this.faceService.registerFace(this.username, this.videoRef.nativeElement);
      this.faceRegistered.emit(success);
    } catch (err) {
      this.error.emit('Failed to register face');
      console.error(err);
    }
  }
}
