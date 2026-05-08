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

  onFaceRegistered(success: boolean): void {
    if (success) {
      // Create the user in the backend too
      this.authService.signup(this.registerUsername, this.role).subscribe({
        next: () => {
          this.registrationSuccess = true;
          this.faceMode = 'login';
          this.registerUsername = '';
          setTimeout(() => {
            this.registrationSuccess = false;
          }, 3000);
        },
        error: (err) => {
          this.faceErrorMessage = 'Face descriptor saved, but failed to create user in database.';
          console.error('Signup error:', err);
        }
      });
    }
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
