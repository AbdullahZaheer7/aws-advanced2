# PixelWave Marketing Image Gallery

Serverless corporate image gallery using:
- **Amplify** (frontend hosting)
- **API Gateway (REST)**
- **Lambda (Python 3.9)**
- **S3** (private bucket; images under `images/` prefix)

## What you get
- A 4-page single-page-HTML UI: **Home, Gallery, About, Contact**
- Gallery calls backend to generate **temporary (5 minute)** pre-signed URLs
- S3 stays **private**: users cannot access S3 objects directly

---

## Folder Contents
- `index.html` — Frontend (vanilla JS, all pages)
- `lambda_function.py` — Lambda code that generates pre-signed URLs
- `template.yaml` — SAM/CloudFormation template
- `Deploy.sh` — helper script for SAM deploy
- `README.md` — instructions

---

## Phase 1: Prerequisites
1. Install **AWS CLI**: https://aws.amazon.com/cli/
2. Install **SAM CLI** (for template deployment): https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
3. Install **Node.js** (only needed if you use Amplify connected repo): https://nodejs.org/
4. Configure AWS CLI:
   ```bash
   aws configure
   ```

---

## Phase 2: Create the private S3 bucket
1. Create bucket in your chosen region (recommended: `us-east-1`)
2. Keep **Block all public access** = ON
3. Enable versioning (optional)
4. Upload images into a folder named `images/`

### Required object keys
Upload these files with these exact names:
- `images/annual-meetup.jpg`
- `images/product-launch.jpg`
- `images/team-building.jpg`
- `images/client-conference.jpg`

### Note
Use a globally unique bucket name, e.g.
`pixelwave-images-<your-name>`

---

## Phase 3: Deploy Lambda + API Gateway (SAM)
1. Open `template.yaml` and keep it as-is.
2. Edit `Deploy.sh`:
   - Set `BUCKET_NAME="your-bucket-name"`
3. Deploy:
   ```bash
   cd PixelWave-Marketing-Image-Gallery
   ./Deploy.sh
   ```

### Get the API endpoint
After deployment, SAM will output the API invoke URL.

You must then update `index.html`:
- Replace `API_URL` in `index.html` with your real endpoint, e.g.
  `https://xxxx.execute-api.us-east-1.amazonaws.com/prod/generate-url`

---

## Phase 4: Host the frontend (Amplify)
### Option A (recommended): Amplify
1. Go to **AWS Amplify** → Get started
2. Connect GitHub repo (or use your local folder in a git repo)
3. Ensure Amplify builds and serves `index.html`
4. Deploy

### Option B: Local testing
You can open `index.html` via a local web server, but note that browsers enforce CORS.
This solution relies on API Gateway CORS being enabled (already configured in SAM).

---

## Phase 5: Test
1. Open your deployed site
2. Go to **Gallery**
3. Click **View Image** for any event photo
4. Confirm:
   - Image loads
   - Timer counts down
   - After 5 minutes, refreshing the image using the old URL should fail

---

## Security verification (important)
Try opening a direct S3 URL like:
`https://<your-bucket>.s3.amazonaws.com/images/annual-meetup.jpg`

You should get **AccessDenied**.

The only access path should be the **Lambda-generated pre-signed URL**.

---

## Troubleshooting
- **CORS error**: ensure API Gateway CORS is enabled for POST and OPTIONS
- **AccessDenied / 403 from Lambda**:
  - Lambda role must have `s3:HeadObject` and `s3:GetObject` on `arn:aws:s3:::<bucket>/images/*`
- **Image not found**:
  - File name must match exactly (case-sensitive)
- **API 500**:
  - Confirm API URL in `index.html`

---

## Quick checklist
- [ ] S3 bucket is private (public access blocked)
- [ ] Images uploaded under `images/` prefix
- [ ] Lambda deployed with `BUCKET_NAME` set
- [ ] API Gateway deployed and reachable
- [ ] `index.html` has correct `API_URL`
- [ ] Gallery generates URLs valid for ~300 seconds

