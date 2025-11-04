from PIL import Image, ImageDraw
import os

def generate_favicon():
    """Generate simple favicon untuk sistem absensi"""
    
    print("🎨 Generating favicon for QR Attendance System...")
    
    # Buat folder static jika belum ada
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Size untuk favicon (16x16, 32x32, 48x48)
    sizes = [(16, 16), (32, 32), (48, 48)]
    
    images = []
    
    for size in sizes:
        # Buat gambar dengan background gradient biru
        img = Image.new('RGB', size, color=(102, 126, 234))  # Warna biru dari gradient
        
        if size[0] >= 32:  # Hanya gambar detail untuk size yang cukup besar
            draw = ImageDraw.Draw(img)
            
            # Gambar kotak QR code style
            margin = 2
            box_size = size[0] // 4
            
            # Sudut kiri atas
            draw.rectangle([margin, margin, margin+box_size, margin+box_size], 
                         fill=(255, 255, 255, 128)) 
            
            # Sudut kanan atas  
            draw.rectangle([size[0]-margin-box_size, margin, size[0]-margin, margin+box_size], 
                         fill=(255, 255, 255, 128))
            
            # Sudut kiri bawah
            draw.rectangle([margin, size[1]-margin-box_size, margin+box_size, size[1]-margin], 
                         fill=(255, 255, 255, 128))
            
            # Titik tengah
            center_size = size[0] // 8
            center_x = (size[0] - center_size) // 2
            center_y = (size[1] - center_size) // 2
            draw.rectangle([center_x, center_y, center_x+center_size, center_y+center_size], 
                         fill=(255, 255, 255, 200))
        
        images.append(img)
    
    # Simpan sebagai favicon.ico (multiple sizes)
    favicon_path = 'static/favicon.ico'
    images[0].save(favicon_path, format='ICO', sizes=[(16,16), (32,32), (48,48)])
    
    print(f"✅ Favicon generated: {favicon_path}")
    print("🎯 Favicon ready for use!")

if __name__ == "__main__":
    generate_favicon()