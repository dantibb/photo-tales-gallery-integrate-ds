"""
Image Metadata Extraction Module

This module provides functions to extract metadata from images including EXIF data,
file information, and other relevant details.
"""

from PIL import Image, ExifTags
import os
from datetime import datetime
import json

def make_json_serializable(obj):
    """Recursively convert non-JSON-serializable objects (like IFDRational) to strings."""
    from PIL.TiffImagePlugin import IFDRational
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, IFDRational):
        try:
            return f"{obj.numerator}/{obj.denominator} ({float(obj):.6f})"
        except Exception:
            return str(obj)
    else:
        try:
            json.dumps(obj)
            return obj
        except Exception:
            return str(obj)

def dms_to_decimal(dms, ref):
    """Convert degrees/minutes/seconds tuple and reference to decimal degrees."""
    try:
        degrees, minutes, seconds = dms
        decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return None

def extract_image_metadata(image_path):
    """
    Extract comprehensive metadata from an image file.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Dictionary containing all available metadata
    """
    metadata = {
        'file_info': {},
        'exif_data': {},
        'gps_data': {},
        'image_info': {}
    }
    
    try:
        with Image.open(image_path) as img:
            # Basic file information
            metadata['file_info'] = {
                'filename': os.path.basename(image_path),
                'file_path': image_path,
                'file_size': os.path.getsize(image_path),
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height
            }
            
            # Image information
            metadata['image_info'] = {
                'dpi': img.info.get('dpi'),
                'compression': img.info.get('compression'),
                'progressive': img.info.get('progressive'),
                'transparency': img.info.get('transparency'),
                'duration': img.info.get('duration'),  # For GIFs
                'loop': img.info.get('loop'),  # For GIFs
                'comment': img.info.get('comment'),
                'icc_profile': bool(img.info.get('icc_profile'))
            }
            
            # EXIF data
            try:
                exif = img.getexif()
                if exif:
                    # Convert EXIF data to readable format
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, f'Unknown Tag {tag_id}')
                        
                        # Handle different data types and convert to JSON-serializable format
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8', errors='ignore')
                            except:
                                value = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                        elif hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                            # Handle IFDRational objects
                            try:
                                if value.denominator != 0:
                                    decimal_value = value.numerator / value.denominator
                                    value = f"{value.numerator}/{value.denominator} ({decimal_value:.2f})"
                                else:
                                    value = f"{value.numerator}/0 (undefined)"
                            except:
                                value = str(value)
                        elif isinstance(value, tuple) and len(value) > 0:
                            # Handle tuples (like GPS coordinates)
                            try:
                                if all(hasattr(v, 'numerator') and hasattr(v, 'denominator') for v in value):
                                    # Convert tuple of IFDRational objects
                                    converted_values = []
                                    for v in value:
                                        if v.denominator != 0:
                                            decimal_val = v.numerator / v.denominator
                                            converted_values.append(f"{v.numerator}/{v.denominator} ({decimal_val:.2f})")
                                        else:
                                            converted_values.append(f"{v.numerator}/0")
                                    value = ", ".join(converted_values)
                                else:
                                    value = str(value)
                            except:
                                value = str(value)
                        else:
                            # Convert any other non-serializable objects to string
                            try:
                                value = str(value)
                            except:
                                value = "Unable to convert value"
                        
                        metadata['exif_data'][tag_name] = value
                    
                    # Extract GPS data if available
                    try:
                        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
                        if gps_ifd:
                            lat = lon = lat_ref = lon_ref = None
                            for tag_id, value in gps_ifd.items():
                                tag_name = ExifTags.GPS.get(tag_id, f'GPS Unknown Tag {tag_id}')
                                # Save for decimal conversion
                                if tag_name == 'GPSLatitude':
                                    lat = value
                                elif tag_name == 'GPSLatitudeRef':
                                    lat_ref = value
                                elif tag_name == 'GPSLongitude':
                                    lon = value
                                elif tag_name == 'GPSLongitudeRef':
                                    lon_ref = value
                                # ... existing code for string conversion ...
                                if tag_name in ['GPSLatitude', 'GPSLongitude'] and isinstance(value, tuple):
                                    try:
                                        converted_values = []
                                        for v in value:
                                            if hasattr(v, 'numerator') and hasattr(v, 'denominator'):
                                                if v.denominator != 0:
                                                    decimal_val = v.numerator / v.denominator
                                                    converted_values.append(decimal_val)
                                                else:
                                                    converted_values.append(0)
                                            else:
                                                converted_values.append(float(v))
                                        # Format as degrees/minutes/seconds if we have 3 values
                                        if len(converted_values) == 3:
                                            value = f"{converted_values[0]}° {converted_values[1]}' {converted_values[2]}\""
                                        else:
                                            value = ", ".join(str(x) for x in converted_values)
                                    except:
                                        value = str(value)
                                else:
                                    if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                                        try:
                                            if value.denominator != 0:
                                                decimal_val = value.numerator / value.denominator
                                                value = f"{value.numerator}/{value.denominator} ({decimal_val:.2f})"
                                            else:
                                                value = f"{value.numerator}/0"
                                        except:
                                            value = str(value)
                                    else:
                                        value = str(value)
                                metadata['gps_data'][tag_name] = value
                            # Add decimal degrees and Google Maps link if possible
                            if lat and lon and lat_ref and lon_ref:
                                # Convert to decimal degrees
                                def to_float_tuple(t):
                                    return [float(v.numerator) / float(v.denominator) if hasattr(v, 'numerator') and hasattr(v, 'denominator') else float(v) for v in t]
                                lat_decimal = dms_to_decimal(to_float_tuple(lat), lat_ref)
                                lon_decimal = dms_to_decimal(to_float_tuple(lon), lon_ref)
                                metadata['gps_data']['Latitude (decimal)'] = lat_decimal
                                metadata['gps_data']['Longitude (decimal)'] = lon_decimal
                                metadata['gps_data']['Google Maps'] = f"https://maps.google.com/?q={lat_decimal},{lon_decimal}"
                    except Exception as gps_error:
                        metadata['gps_data']['error'] = f"Failed to extract GPS data: {str(gps_error)}"
            except Exception as e:
                metadata['exif_data']['error'] = f"Failed to extract EXIF data: {str(e)}"
                
    except Exception as e:
        metadata['error'] = f"Failed to open image: {str(e)}"
    
    return make_json_serializable(metadata)

def format_metadata_for_display(metadata):
    """
    Format metadata for display in the UI.
    
    Args:
        metadata (dict): Raw metadata dictionary
        
    Returns:
        dict: Formatted metadata organized by sections
    """
    formatted = {
        'file_info': {},
        'camera_info': {},
        'capture_info': {},
        'technical_info': {},
        'gps_info': {},
        'other_info': {}
    }
    
    # File information
    if 'file_info' in metadata:
        formatted['file_info'] = {
            'Filename': metadata['file_info'].get('filename', 'Unknown'),
            'File Size': f"{metadata['file_info'].get('file_size', 0) / 1024:.1f} KB",
            'Format': metadata['file_info'].get('format', 'Unknown'),
            'Dimensions': f"{metadata['file_info'].get('width', 0)} × {metadata['file_info'].get('height', 0)} pixels",
            'Color Mode': metadata['file_info'].get('mode', 'Unknown')
        }
    
    # Camera information
    camera_tags = {
        'Make': 'Camera Make',
        'Model': 'Camera Model',
        'Software': 'Software',
        'Artist': 'Artist',
        'Copyright': 'Copyright'
    }
    
    for tag, display_name in camera_tags.items():
        if tag in metadata.get('exif_data', {}):
            formatted['camera_info'][display_name] = metadata['exif_data'][tag]
    
    # Capture information
    capture_tags = {
        'DateTime': 'Date & Time',
        'DateTimeOriginal': 'Original Date & Time',
        'DateTimeDigitized': 'Digitized Date & Time',
        'ImageDescription': 'Description',
        'UserComment': 'User Comment'
    }
    
    for tag, display_name in capture_tags.items():
        if tag in metadata.get('exif_data', {}):
            formatted['capture_info'][display_name] = metadata['exif_data'][tag]
    
    # Technical information
    technical_tags = {
        'ExposureTime': 'Exposure Time',
        'FNumber': 'F-Number',
        'ISOSpeedRatings': 'ISO Speed',
        'FocalLength': 'Focal Length',
        'Flash': 'Flash',
        'WhiteBalance': 'White Balance',
        'MeteringMode': 'Metering Mode',
        'ExposureProgram': 'Exposure Program',
        'ExposureMode': 'Exposure Mode',
        'DigitalZoomRatio': 'Digital Zoom',
        'SceneCaptureType': 'Scene Type',
        'GainControl': 'Gain Control',
        'Contrast': 'Contrast',
        'Saturation': 'Saturation',
        'Sharpness': 'Sharpness'
    }
    
    for tag, display_name in technical_tags.items():
        if tag in metadata.get('exif_data', {}):
            formatted['technical_info'][display_name] = metadata['exif_data'][tag]
    
    # GPS information
    if metadata.get('gps_data'):
        gps_display_names = {
            'GPSLatitude': 'Latitude',
            'GPSLongitude': 'Longitude',
            'GPSAltitude': 'Altitude',
            'GPSDateStamp': 'GPS Date',
            'GPSTimeStamp': 'GPS Time',
            'GPSProcessingMethod': 'Processing Method'
        }
        
        for tag, display_name in gps_display_names.items():
            if tag in metadata['gps_data']:
                formatted['gps_info'][display_name] = metadata['gps_data'][tag]
    
    # Other information
    other_tags = ['Orientation', 'ColorSpace', 'ComponentsConfiguration', 'CompressedBitsPerPixel']
    for tag in other_tags:
        if tag in metadata.get('exif_data', {}):
            formatted['other_info'][tag] = metadata['exif_data'][tag]
    
    return formatted

def get_metadata_summary(metadata):
    """
    Get a brief summary of the most important metadata.
    
    Args:
        metadata (dict): Raw metadata dictionary
        
    Returns:
        str: Summary string
    """
    summary_parts = []
    
    # Camera info
    if 'Make' in metadata.get('exif_data', {}):
        make = metadata['exif_data']['Make']
        model = metadata['exif_data'].get('Model', '')
        summary_parts.append(f"Camera: {make} {model}".strip())
    
    # Date
    for date_tag in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']:
        if date_tag in metadata.get('exif_data', {}):
            summary_parts.append(f"Date: {metadata['exif_data'][date_tag]}")
            break
    
    # Technical details
    if 'ExposureTime' in metadata.get('exif_data', {}):
        summary_parts.append(f"Exposure: {metadata['exif_data']['ExposureTime']}")
    
    if 'FNumber' in metadata.get('exif_data', {}):
        summary_parts.append(f"F-Number: {metadata['exif_data']['FNumber']}")
    
    if 'ISOSpeedRatings' in metadata.get('exif_data', {}):
        summary_parts.append(f"ISO: {metadata['exif_data']['ISOSpeedRatings']}")
    
    # GPS
    if metadata.get('gps_data'):
        summary_parts.append("GPS: Available")
    
    return " | ".join(summary_parts) if summary_parts else "No metadata available" 