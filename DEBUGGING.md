# Debugging Guide for SlideSpark AI

## How to Debug Issues

### 1. Check Browser Console
Open your browser's Developer Tools (F12 or right-click → Inspect) and check the Console tab for JavaScript errors.

### 2. Check Flask Logs
Monitor the Flask app logs in real-time:
```bash
tail -f app.log
```

### 3. Common Issues and Solutions

#### Issue: "Structure Explorer is empty after upload"
**Solution**: 
1. Check browser console for errors
2. Verify the upload response contains a structure
3. Make sure JavaScript is enabled

#### Issue: "Execute button doesn't work"
**Solution**:
1. You must select a shape first (click on a shape in the Structure Explorer)
2. Check the console output for error messages
3. The selected shape will be highlighted in blue

#### Issue: "No slide preview"
**Solution**:
1. LibreOffice might not be installed - you'll see a placeholder image
2. Check if the slide navigation buttons work
3. Try clicking different slides

## Usage Instructions

1. **Upload a Presentation**:
   - Click "Upload Presentation"
   - Select a .pptx file
   - Wait for "Presentation uploaded successfully!"
   - The structure should appear in the left panel

2. **Edit a Shape**:
   - Click on a shape in the Structure Explorer (it will turn blue)
   - Type a command like "Make the text bold and larger"
   - Click "Execute"
   - Check the console for feedback

3. **Try Different Commands**:
   - "Change the color to red"
   - "Make the font size 24pt"
   - "Add emphasis to this text"
   - "Make this title consistent with others" (use Global Context)

## Testing the Fix

Try these steps in order:
1. Refresh the page (Ctrl+R or Cmd+R)
2. Upload test_presentation.pptx
3. Open browser console to see debug logs
4. Click on a shape in the Structure Explorer
5. Enter a command and click Execute

The console will show:
- Upload response data
- Structure rendering logs
- Command execution details
- Any errors that occur