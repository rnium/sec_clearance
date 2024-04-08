from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from pathlib import Path
from PIL import Image
from io import BytesIO


def validate_image_extension(value):
    valid_extensions = ['.'+n for n in settings.ALLOWED_IMAGE_EXTENSIONS]
    ext = Path(value.name).suffix
    if not ext.lower() in valid_extensions:
        raise ValidationError('Invalid file type. Allowed file types are: {}'.format(', '.join(valid_extensions)))


def compress_image(image):
    try:
        validate_image_extension(image)
    except ValidationError as e:
        raise ValidationError(e)
    img = Image.open(image)
    width, height = img.size
    # Calculate the dimensions of the center portion to be cropped
    crop_width = crop_height = min(width, height)

    # Calculate the left, upper, right, and lower coordinates of the center portion
    left = (width - crop_width) // 2
    upper = (height - crop_height) // 2
    right = left + crop_width
    lower = upper + crop_height

    # Crop the center portion of the image
    center_cropped_image = img.crop((left, upper, right, lower))
    formatted_img = center_cropped_image.resize((500,500))
    img_format = img.format.lower()
    img_io = BytesIO()
    formatted_img.save(img_io, format=img_format, quality=50)
    img_file = ContentFile(img_io.getvalue())

    if hasattr(image, 'name') and image.name:
        img_file.name = image.name

    if hasattr(image, 'content_type') and image.content_type:
        img_file.content_type = image.content_type

    if hasattr(image, 'size') and image.size:
        img_file.size = image.size

    if hasattr(image, 'charset') and image.charset:
        img_file.charset = image.charset

    if hasattr(image, '_committed') and image._committed:
        img_file._committed = image._committed

    return img_file


def get_userinfo_data(request):
    data = {
        'is_authenticated': False,
        'username': '',
        'user_fullname': '',
        'account_type': '',
        'user_type': '',
    }
    if request.user.is_authenticated:
        data['is_authenticated'] = True
    if hasattr(request.user, 'adminaccount'):
        admin_ac = request.user.adminaccount
        data['account_type'] = 'admin'
        data['user_type'] = admin_ac.user_type
        data['user_fullname'] = admin_ac.full_name
    if hasattr(request.user, 'studentaccount'):
        student_ac = request.user.studentaccount
        data['account_type'] = 'student'
        data['user_fullname'] = student_ac.full_name
    return data
    