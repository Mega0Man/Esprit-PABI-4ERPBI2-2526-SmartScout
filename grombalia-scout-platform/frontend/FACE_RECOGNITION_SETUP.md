# Face Recognition Setup Instructions

To make the facial recognition feature work, you need to download the face-api.js models and place them in the `public/models/` directory.

## Step 1: Download the Models

Download the model files from this repository:
https://github.com/justadudewhohacks/face-api.js/tree/master/weights

You need these files:
1. `tiny_face_detector_model-shard1`
2. `tiny_face_detector_model-weights_manifest.json`
3. `face_landmark_68_model-shard1`
4. `face_landmark_68_model-weights_manifest.json`
5. `face_recognition_model-shard1`
6. `face_recognition_model-shard2`
7. `face_recognition_model-weights_manifest.json`
8. `face_expression_model-shard1`
9. `face_expression_model-weights_manifest.json`

## Step 2: Place the Files

Put all downloaded files into:
```
grombalia-scout-platform/frontend/public/models/
```

## Step 3: Run the App

Now you can run the Angular app normally:
```bash
npm start
```

## How to Use

1. Go to any login page
2. Click on "👤 Face ID" tab
3. To register a new face:
   - Click "📝 Register New Face"
   - Enter your username
   - Position your face in the camera
   - Click "📸 Register Face"
4. To login with face:
   - Just position your face in the camera
   - It will automatically recognize you and log you in!

## Notes

- All face data is stored locally in your browser's localStorage
- No data is sent to any server (everything stays in the browser!)
- You need to allow camera access when prompted
