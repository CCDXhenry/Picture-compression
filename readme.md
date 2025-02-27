# Image Compression Tool

This tool allows you to compress images to a specified target size in kilobytes (KB). It supports JPEG and PNG formats and can process both individual files and entire directories.

## Usage

1. **Install Dependencies**:
   Make sure you have Python installed, then install the required packages by running:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Script**:
   Execute the script by running:
   ```bash
   python src/compress.py
   ```

3. **Follow the Prompts**:
   - **Input Path**: Provide the path to the image file or directory containing images.
   - **Output Path**: Provide the path where the compressed image(s) will be saved.
   - **Target Size (KB)**: Specify the desired file size in KB.
   - **Minimum Quality (Optional)**: Set the minimum quality for the compression (default is 5).

## Example

```bash
python src/compress.py
```

- **Input Path**: `images/input.jpg`
- **Output Path**: `images/output.jpg`
- **Target Size (KB)**: `100`
- **Minimum Quality**: `10`

This will compress `input.jpg` to approximately 100KB and save it as `output.jpg`.

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

## Notes

- If the input image is already smaller than the target size, it will be saved without further compression.
- The script uses a binary search algorithm to find the optimal quality setting to achieve the target size.