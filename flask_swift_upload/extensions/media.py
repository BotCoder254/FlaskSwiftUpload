"""Professional media processing extensions for FlaskSwiftUpload.

░█▀▀░█░░░█▀█░█▀▀░█░█░░░█▄█░█▀▀░█▀▄░▀█▀░█▀█
░█▀▀░█░░░█▀█░▀▀█░█▀▄░░░█░█░█▀▀░█░█░░█░░█▀█
░▀░░░▀▀▀░▀░▀░▀▀▀░▀░▀░░░▀░▀░▀▀▀░▀▀░░▀▀▀░▀░▀
░█▀▀░█░█░▀█▀░█▀▀░█▀█░█▀▀░▀█▀░█▀█░█▀█░█▀▀
░█▀▀░▄▀▄░░█░░█▀▀░█░█░▀▀█░░█░░█░█░█░█░▀▀█
░▀▀▀░▀░▀░░▀░░▀▀▀░▀░▀░▀▀▀░░▀░░▀▀▀░▀░▀░▀▀▀
"""

import os
from typing import Optional, Dict, List, Tuple, Union
from pathlib import Path
import asyncio
from PIL import Image
import ffmpeg
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

@dataclass
class ImageProcessingConfig:
    """Configuration for image processing."""
    max_dimensions: Tuple[int, int] = (1920, 1080)
    quality: int = 85
    format: str = 'JPEG'
    create_thumbnails: bool = True
    thumbnail_sizes: List[Tuple[int, int]] = None
    preserve_exif: bool = True
    optimize: bool = True
    progressive: bool = True

@dataclass
class VideoProcessingConfig:
    """Configuration for video processing."""
    max_resolution: str = '1920x1080'
    codec: str = 'libx264'
    preset: str = 'medium'
    crf: int = 23
    audio_codec: str = 'aac'
    audio_bitrate: str = '128k'
    create_preview: bool = True
    preview_duration: int = 10
    thumbnail_time: int = 5

class MediaProcessor:
    """Professional media processing with advanced features."""

    def __init__(
        self,
        image_config: Optional[ImageProcessingConfig] = None,
        video_config: Optional[VideoProcessingConfig] = None,
        max_workers: int = 4
    ):
        """Initialize the media processor.
        
        Args:
            image_config: Configuration for image processing
            video_config: Configuration for video processing
            max_workers: Maximum number of concurrent workers
        """
        self.image_config = image_config or ImageProcessingConfig()
        self.video_config = video_config or VideoProcessingConfig()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_image(
        self,
        input_path: Union[str, Path],
        output_dir: Union[str, Path],
        options: Optional[Dict] = None
    ) -> Dict:
        """Process an image with professional features.
        
        Args:
            input_path: Path to input image
            output_dir: Output directory
            options: Optional processing options
            
        Returns:
            Dict: Processing results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._process_image_sync,
            input_path,
            output_dir,
            options or {}
        )

    def _process_image_sync(
        self,
        input_path: Union[str, Path],
        output_dir: Union[str, Path],
        options: Dict
    ) -> Dict:
        """Synchronous image processing (runs in thread pool).
        
        Args:
            input_path: Path to input image
            output_dir: Output directory
            options: Processing options
            
        Returns:
            Dict: Processing results
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            with Image.open(input_path) as img:
                # Preserve EXIF if configured
                exif = img.info.get('exif') if self.image_config.preserve_exif else None
                
                # Process main image
                processed = self._resize_image(img, self.image_config.max_dimensions)
                main_output = output_dir / f"processed_{input_path.name}"
                
                processed.save(
                    main_output,
                    format=self.image_config.format,
                    quality=self.image_config.quality,
                    optimize=self.image_config.optimize,
                    progressive=self.image_config.progressive,
                    exif=exif
                )

                results = {
                    'main_image': {
                        'path': str(main_output),
                        'size': main_output.stat().st_size,
                        'dimensions': processed.size
                    }
                }

                # Generate thumbnails if configured
                if self.image_config.create_thumbnails:
                    thumbnails = self._create_thumbnails(
                        img,
                        output_dir,
                        input_path.stem,
                        self.image_config.thumbnail_sizes or [(150, 150), (300, 300)]
                    )
                    results['thumbnails'] = thumbnails

                return results

        except Exception as e:
            logger.error(f"Error processing image {input_path}: {str(e)}")
            raise

    def _resize_image(self, img: Image.Image, max_dimensions: Tuple[int, int]) -> Image.Image:
        """Resize image maintaining aspect ratio.
        
        Args:
            img: PIL Image object
            max_dimensions: Maximum dimensions
            
        Returns:
            Image.Image: Resized image
        """
        ratio = min(max_dimensions[0] / img.width, max_dimensions[1] / img.height)
        if ratio < 1:
            new_size = (int(img.width * ratio), int(img.height * ratio))
            return img.resize(new_size, Image.LANCZOS)
        return img

    def _create_thumbnails(
        self,
        img: Image.Image,
        output_dir: Path,
        basename: str,
        sizes: List[Tuple[int, int]]
    ) -> Dict:
        """Create image thumbnails.
        
        Args:
            img: PIL Image object
            output_dir: Output directory
            basename: Base filename
            sizes: List of thumbnail sizes
            
        Returns:
            Dict: Thumbnail information
        """
        thumbnails = {}
        for size in sizes:
            thumb = img.copy()
            thumb.thumbnail(size)
            
            filename = f"thumb_{size[0]}x{size[1]}_{basename}.jpg"
            thumb_path = output_dir / filename
            
            thumb.save(
                thumb_path,
                'JPEG',
                quality=85,
                optimize=True
            )
            
            thumbnails[f"{size[0]}x{size[1]}"] = {
                'path': str(thumb_path),
                'size': thumb_path.stat().st_size,
                'dimensions': thumb.size
            }
            
        return thumbnails

    async def process_video(
        self,
        input_path: Union[str, Path],
        output_dir: Union[str, Path],
        options: Optional[Dict] = None
    ) -> Dict:
        """Process a video with professional features.
        
        Args:
            input_path: Path to input video
            output_dir: Output directory
            options: Optional processing options
            
        Returns:
            Dict: Processing results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._process_video_sync,
            input_path,
            output_dir,
            options or {}
        )

    def _process_video_sync(
        self,
        input_path: Union[str, Path],
        output_dir: Union[str, Path],
        options: Dict
    ) -> Dict:
        """Synchronous video processing (runs in thread pool).
        
        Args:
            input_path: Path to input video
            output_dir: Output directory
            options: Processing options
            
        Returns:
            Dict: Processing results
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Get video information
            probe = ffmpeg.probe(str(input_path))
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            # Process main video
            output_path = output_dir / f"processed_{input_path.name}"
            
            stream = ffmpeg.input(str(input_path))
            
            stream = ffmpeg.output(
                stream,
                str(output_path),
                vcodec=self.video_config.codec,
                acodec=self.video_config.audio_codec,
                video_bitrate=options.get('video_bitrate', '2000k'),
                audio_bitrate=self.video_config.audio_bitrate,
                preset=self.video_config.preset,
                crf=self.video_config.crf,
                vf=f"scale={self.video_config.max_resolution}:force_original_aspect_ratio=decrease"
            )
            
            ffmpeg.run(stream, overwrite_output=True)

            results = {
                'main_video': {
                    'path': str(output_path),
                    'size': output_path.stat().st_size,
                    'duration': float(probe['format']['duration']),
                    'resolution': f"{video_info['width']}x{video_info['height']}"
                }
            }

            # Generate preview if configured
            if self.video_config.create_preview:
                preview = self._create_video_preview(
                    input_path,
                    output_dir,
                    self.video_config.preview_duration
                )
                results['preview'] = preview

            # Generate thumbnail
            thumbnail = self._create_video_thumbnail(
                input_path,
                output_dir,
                self.video_config.thumbnail_time
            )
            results['thumbnail'] = thumbnail

            return results

        except Exception as e:
            logger.error(f"Error processing video {input_path}: {str(e)}")
            raise

    def _create_video_preview(
        self,
        input_path: Path,
        output_dir: Path,
        duration: int
    ) -> Dict:
        """Create a video preview clip.
        
        Args:
            input_path: Path to input video
            output_dir: Output directory
            duration: Preview duration in seconds
            
        Returns:
            Dict: Preview information
        """
        preview_path = output_dir / f"preview_{input_path.name}"
        
        stream = ffmpeg.input(str(input_path))
        stream = ffmpeg.output(
            stream,
            str(preview_path),
            t=duration,
            vcodec=self.video_config.codec,
            acodec=self.video_config.audio_codec,
            preset='fast',
            crf=28
        )
        
        ffmpeg.run(stream, overwrite_output=True)
        
        return {
            'path': str(preview_path),
            'size': preview_path.stat().st_size,
            'duration': duration
        }

    def _create_video_thumbnail(
        self,
        input_path: Path,
        output_dir: Path,
        timestamp: int
    ) -> Dict:
        """Create a video thumbnail.
        
        Args:
            input_path: Path to input video
            output_dir: Output directory
            timestamp: Timestamp for thumbnail in seconds
            
        Returns:
            Dict: Thumbnail information
        """
        thumb_path = output_dir / f"thumb_{input_path.stem}.jpg"
        
        stream = ffmpeg.input(str(input_path), ss=timestamp)
        stream = ffmpeg.output(
            stream,
            str(thumb_path),
            vframes=1,
            format='image2'
        )
        
        ffmpeg.run(stream, overwrite_output=True)
        
        return {
            'path': str(thumb_path),
            'size': thumb_path.stat().st_size
        }
