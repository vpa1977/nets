import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.awt.image.WritableRaster;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

import javax.imageio.ImageIO;

public class ImageHelper {
	
	public static byte[] extractBytes (String ImageName) throws IOException {
		 // open image
		 File imgPath = new File(ImageName);
		 BufferedImage bufferedImage = ImageIO.read(imgPath);

		 // get DataBufferBytes from Raster
		 WritableRaster raster = bufferedImage .getRaster();
		 DataBufferByte data   = (DataBufferByte) raster.getDataBuffer();

		 return ( data.getData() );
	}
	

	public static void main(String[] args) throws Throwable{
		byte[] list = extractBytes(args[0]);
		FileOutputStream fos = new FileOutputStream(args[1]);
		fos.write(list);
		fos.close();
	}

}
