import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { FaceRecognitionComponent } from '../face-recognition/face-recognition.component';

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
  
  activeTab: 'password' | 'face' = 'password';
  faceMode: 'login' | 'register' = 'login';
  registerUsername: string = '';
  registerPassword: string = '';
  registerId: string = '';
  faceCaptured: boolean = false;
  currentDescriptor: number[] | null = null;
  faceErrorMessage: string = '';
  registrationSuccess: boolean = false;

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
    private authService: AuthService
  ) { }

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
    this.loading = true;
    this.faceErrorMessage = '';

    this.authService.loginByFace(username).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.user.role === this.role) {
          this.router.navigate([`/dashboard/${this.role}`]);
        } else {
          this.faceErrorMessage = 'Invalid role for this user';
          this.authService.logout();
        }
      },
      error: (err) => {
        this.loading = false;
        this.faceErrorMessage = 'Face recognized as ' + username + ' but login failed. Ensure user exists in database.';
      }
    });
  }

  onFaceDetected(detection: any): void {
    if (detection && detection.descriptor) {
      this.currentDescriptor = Array.from(detection.descriptor);
    }
  }

  onFaceRegistered(success: boolean): void {
    if (success && this.currentDescriptor) {
      // Validate inputs before signup
      if (this.registerId.length !== 8) {
        this.faceErrorMessage = 'National ID must be exactly 8 digits.';
        return;
      }
      if (!this.registerUsername || !this.registerPassword) {
        this.faceErrorMessage = 'Username and password are required.';
        return;
      }

      this.loading = true;
      this.faceErrorMessage = '';

      const signupData = {
        username: this.registerUsername,
        password: this.registerPassword,
        role: this.role,
        national_id: this.registerId,
        face_descriptor: this.currentDescriptor
      };

      this.authService.signup(signupData).subscribe({
        next: () => {
          this.loading = false;
          this.registrationSuccess = true;
          this.faceMode = 'login';
          this.resetRegisterForm();
          setTimeout(() => {
            this.registrationSuccess = false;
          }, 3000);
        },
        error: (err) => {
          this.loading = false;
          this.faceErrorMessage = err.error?.detail || 'Registration failed. Check if username/ID is already taken or invalid.';
          console.error('Signup error:', err);
        }
      });
    }
  }

  private resetRegisterForm(): void {
    this.registerUsername = '';
    this.registerPassword = '';
    this.registerId = '';
    this.currentDescriptor = null;
    this.faceCaptured = false;
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
