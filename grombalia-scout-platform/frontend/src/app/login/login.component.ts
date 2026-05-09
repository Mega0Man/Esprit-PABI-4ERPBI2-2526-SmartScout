import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { FaceRecognitionComponent } from '../face-recognition/face-recognition.component';
import { LanguageService, Lang } from '../services/language.service';
import { AudioService } from '../services/audio.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  @ViewChild(FaceRecognitionComponent) faceRecognitionComponent?: FaceRecognitionComponent;
  
  loginForm!: FormGroup;
  role!: string;
  roleConfig: any;
  error: string = '';
  loading: boolean = false;
  currentLang$ = this.languageService.currentLang$;
  
  activeTab: 'password' | 'face' = 'password';
  faceMode: 'login' | 'register' = 'login';
  registerUsername: string = '';
  registerPassword: string = '';
  registerId: string = '';
  faceCaptured: boolean = false;
  enableFaceCapture: boolean = true;
  currentDescriptor: number[] | null = null;
  faceErrorMessage: string = '';
  registrationMessage: string = '';

  roleConfigs = {
    group_leader: {
      name: 'Group Leader',
      color: '#2c7fb8',
      gradientFrom: '#1a3a52',
      gradientTo: '#0d2840',
      lightColor: '#5aa0e6',
      icon: '👥'
    },
    treasurer: {
      name: 'Treasurer',
      color: '#d4af37',
      gradientFrom: '#524a1a',
      gradientTo: '#40350d',
      lightColor: '#f0d78c',
      icon: '💰'
    },
    unit_leader: {
      name: 'Unit Leader',
      color: '#2d8c59',
      gradientFrom: '#1a523a',
      gradientTo: '#0d4028',
      lightColor: '#5cb885',
      icon: '🎯'
    }
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private authService: AuthService,
    private languageService: LanguageService,
    private audioService: AudioService
  ) { }

  getTranslation(key: string): string {
    return this.languageService.translate(key);
  }

  getAudioText(lang: Lang): string {
    const key = this.faceMode === 'register' ? 'register' : 'login';
    return this.audioService.getAudioText(key, lang);
  }

  setLang(lang: Lang): void {
    this.audioService.stop();
    this.languageService.setLanguage(lang);
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.role = params['role'];
      this.roleConfig = this.roleConfigs[this.role as keyof typeof this.roleConfigs];
      if (!this.roleConfig) {
        this.router.navigate(['/']);
      }
    });

    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    const { username, password } = this.loginForm.value;

    this.authService.login(username, password).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.user.role === this.role) {
          this.router.navigate([`/dashboard/${this.role}`]);
        } else {
          this.error = 'Invalid role for this login page';
          this.authService.logout();
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Invalid username or password';
      }
    });
  }

  onFaceRecognized(username: string): void {
    console.log('Face recognized for:', username);
    this.loading = true;
    this.faceErrorMessage = '';

    this.authService.loginByFace(username).subscribe({
      next: (response) => {
        console.log('Face login successful:', response);
        this.loading = false;
        if (response.user.role === this.role) {
          this.router.navigate([`/dashboard/${this.role}`]);
        } else {
          this.faceErrorMessage = `Invalid role for this user (Expected ${this.role}, got ${response.user.role})`;
          this.authService.logout();
        }
      },
      error: (err) => {
        this.loading = false;
        console.error('Face login error:', err);
        this.faceErrorMessage = 'Face recognized as ' + username + ' but login failed. Ensure user exists in database and role matches.';
      }
    });
  }

  toggleFaceCapture(): void {
    this.enableFaceCapture = !this.enableFaceCapture;
    if (!this.enableFaceCapture) {
      this.currentDescriptor = null;
      this.faceCaptured = false;
    }
  }

  onFaceDetected(detection: any): void {
    if (detection && detection.descriptor) {
      this.currentDescriptor = Array.from(detection.descriptor);
    }
  }

  onFaceRegistered(success: boolean): void {
    if (success && this.currentDescriptor) {
      this.faceCaptured = true;
      this.faceErrorMessage = ''; // Clear errors on success
    }
  }

  onSignupSubmit(): void {
    // Validate inputs before signup
    if (this.registerId.length !== 8) {
      this.faceErrorMessage = 'National ID must be exactly 8 digits.';
      return;
    }
    if (!this.registerUsername || !this.registerPassword) {
      this.faceErrorMessage = 'Username and password are required.';
      return;
    }
    if (this.enableFaceCapture && !this.currentDescriptor) {
      this.faceErrorMessage = 'Please capture your face or disable face recognition to proceed.';
      return;
    }

    this.loading = true;
    this.faceErrorMessage = '';

    const signupData = {
      username: this.registerUsername,
      password: this.registerPassword,
      role: this.role,
      national_id: this.registerId,
      face_descriptor: this.enableFaceCapture && this.currentDescriptor ? this.currentDescriptor : undefined
    };

    this.authService.signup(signupData).subscribe({
      next: () => {
        this.registrationMessage = this.enableFaceCapture 
          ? '✅ Account created! Logging you in...' 
          : '✅ Account created! Logging you in...';
        
        // Auto-login after signup
        setTimeout(() => {
          this.authService.login(this.registerUsername, this.registerPassword).subscribe({
            next: (response) => {
              this.loading = false;
              this.router.navigate([`/dashboard/${this.role}`]);
            },
            error: (err) => {
              this.loading = false;
              this.faceMode = 'login';
              this.resetRegisterForm();
              this.registrationMessage = '✅ Account created! Please log in manually.';
            }
          });
        }, 1500);
      },
      error: (err) => {
        this.loading = false;
        this.faceErrorMessage = err.error?.detail || 'Registration failed. Check if username/ID is already taken or invalid.';
        console.error('Signup error:', err);
      }
    });
  }

  private resetRegisterForm(): void {
    this.registerUsername = '';
    this.registerPassword = '';
    this.registerId = '';
    this.currentDescriptor = null;
    this.faceCaptured = false;
    this.enableFaceCapture = true;
  }

  onFaceError(error: string): void {
    this.faceErrorMessage = error;
  }

  registerFace(): void {
    if (this.faceRecognitionComponent) {
      this.faceRecognitionComponent.registerFace();
    }
  }

  goHome(): void {
    this.router.navigate(['/']);
  }
}
