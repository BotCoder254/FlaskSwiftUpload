"""Constants and configurations for FlaskSwiftUpload."""

LOGO = '''
███████╗██╗      █████╗ ███████╗██╗  ██╗    ███████╗██╗    ██╗██╗███████╗████████╗
██╔════╝██║     ██╔══██╗██╔════╝██║ ██╔╝    ██╔════╝██║    ██║██║██╔════╝╚══██╔══╝
█████╗  ██║     ███████║███████╗█████╔╝     ███████╗██║ █╗ ██║██║█████╗     ██║   
██╔══╝  ██║     ██╔══██║╚════██║██╔═██╗     ╚════██║██║███╗██║██║██╔══╝     ██║   
██║     ███████╗██║  ██║███████║██║  ██╗    ███████║╚███╔███╔╝██║██║        ██║   
╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝        ╚═╝   
██╗   ██╗██████╗ ██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗ 
██║   ██║██╔══██╗██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║   ██║██████╔╝██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝
██║   ██║██╔═══╝ ██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗
╚██████╔╝██║     ███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║
 ╚═════╝ ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝'''

# Common MIME types grouped by category
MIME_TYPES = {
    'images': {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/gif': ['.gif'],
        'image/webp': ['.webp'],
        'image/svg+xml': ['.svg'],
        'image/tiff': ['.tiff', '.tif'],
    },
    'documents': {
        'application/pdf': ['.pdf'],
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'application/vnd.ms-excel': ['.xls'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        'application/vnd.ms-powerpoint': ['.ppt'],
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    },
    'archives': {
        'application/zip': ['.zip'],
        'application/x-rar-compressed': ['.rar'],
        'application/x-7z-compressed': ['.7z'],
        'application/x-tar': ['.tar'],
        'application/gzip': ['.gz'],
    },
    'text': {
        'text/plain': ['.txt'],
        'text/csv': ['.csv'],
        'text/html': ['.html', '.htm'],
        'text/css': ['.css'],
        'application/json': ['.json'],
        'application/xml': ['.xml'],
    },
    'audio': {
        'audio/mpeg': ['.mp3'],
        'audio/wav': ['.wav'],
        'audio/ogg': ['.ogg'],
        'audio/aac': ['.aac'],
    },
    'video': {
        'video/mp4': ['.mp4'],
        'video/mpeg': ['.mpeg', '.mpg'],
        'video/quicktime': ['.mov'],
        'video/webm': ['.webm'],
    }
}

# Security settings
SECURITY = {
    'max_filename_length': 255,
    'forbidden_chars': '<>:"/\\|?*\x00-\x1f',
    'forbidden_extensions': ['.php', '.exe', '.sh', '.bat', '.dll', '.so'],
    'scan_content': True,
    'max_path_length': 4096,
}

# Default storage settings
STORAGE = {
    'default_chunk_size': 8192,  # 8KB chunks for file operations
    'temp_prefix': '_temp_',
    'backup_suffix': '_backup_',
    'date_format': '%Y%m%d_%H%M%S',
    'default_permissions': 0o644,  # Default file permissions
    'dir_permissions': 0o755,     # Default directory permissions
}

# Validation settings
VALIDATION = {
    'min_size': 1,                    # 1 byte
    'default_max_size': 16777216,     # 16MB
    'content_check_size': 8192,       # First 8KB for content validation
    'mime_check_size': 2048,          # First 2KB for MIME detection
    'hash_algorithm': 'sha256',       # Default hash algorithm
    'hash_length': 12,                # Length of hash in filename
}
