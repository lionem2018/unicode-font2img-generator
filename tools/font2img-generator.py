import argparse
import glob
import io
import os
import numpy

from PIL import Image, ImageFont, ImageDraw
from fontTools.ttLib import TTFont

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

# Default data paths.
DEFAULT_FONTS_DIR = os.path.join(SCRIPT_PATH, '../fonts')
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_PATH, '../image-data')

# Number of random distortion images to generate per font and character.
# 글꼴 및 문자 당 생성할 랜덤한 왜곡 이미지의 수
DISTORTION_COUNT = 3

# Width and height of the resulting image.
# 결과 이미지의 높이 너비
IMAGE_WIDTH = 64
IMAGE_HEIGHT = 64


def char_in_font(unicode_char, font):
    """
    Check whether the character is existing in font
    해당 글자가 폰트 내에 존재하는지 확인

    :param unicode_char: int, unicode of a character you want check
    :param font: TTFont class, font style
    :return: boolean
    """

    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            if unicode_char in cmap.cmap:
                return True

    return False


def generate_hangul_images(fonts_dir, output_dir, start_unicode=0, end_unicode=0x10FFFF):
    """Generate Hangul image files.  한글 이미지 파일 생성

    This will take in the passed in labels file and will generate several
    images using the font files provided in the font directory. The font
    directory is expected to be populated with *.ttf (True Type Font) files.
    The generated images will be stored in the given output directory. Image
    paths will have their corresponding labels listed in a CSV file.
    전달된 레이블 파일을 받아들여 글꼴 디렉토리에 제공된 글꼴 파일을 사용하여 여러 이미지를 생성합니다.
    글꼴 디렉토리는 * .ttf (True Type Font) 파일로 채워질 것으로 예상됩니다.
    생성된 이미지는 주어진 출력 디렉토리에 저장됩니다. 이미지 경로는 해당 레이블을 CSV 파일에 나열합니다.
    """

    # image 생성 디렉토리 지정 및 생성
    image_dir = os.path.join(output_dir, 'test-images')
    if not os.path.exists(image_dir):
        os.makedirs(os.path.join(image_dir))

    # Get a list of the fonts.
    # ttf 파일 리스트 생성
    fonts = glob.glob(os.path.join(fonts_dir, '*.ttf'))

    # 각 ttf파일들을 통해 생성한 글자 이미지와 레이블 맵핑한 csv 파일 생성
    labels_csv = io.open(os.path.join(output_dir, 'test-labels-map.csv'), 'w',
                         encoding='utf-8')

    # 총 생성된 이미지의 수를 세기 위한 변수
    total_count = 0
    prev_count = 0

    # 각 글자 이미지를 생성할 폰트 수 만큼 반복
    for fontpath in fonts:

        current_count = 0

    # fontpath = fonts[3]

        # 폰트 유니코드 확인을 위해 TTFont로 load
        font = TTFont(fontpath)
        # 해당 폰트의 지원 유니코드 리스트 생성
        unicode_list = []
        for character in range(start_unicode, end_unicode):
            if char_in_font(character, font):
                unicode_list.append(character)

        # 유니코드 테이블이 잘 생성되었는지 출력
        print(unicode_list)
        print("Total number of existing unicode:", len(unicode_list))

        # 유니코드 테이블을 순회하며 이미지 생성
        for unicode in unicode_list:

            # 현재까지 몇 개의 이미지가 생성되었는지 5000개가 생성될 때마다 출력
            if total_count - prev_count > 5000:
                prev_count = total_count
                print('{} images generated...'.format(total_count))

            # 유니코드를 문자로 변경
            character = chr(unicode)
            # 흑백모드('L')의 64*64 이미지 생성
            image = Image.new('L', (IMAGE_WIDTH, IMAGE_HEIGHT), color=0)
            # 트루 타입의 폰트 파일(ttf)을 48 사이즈로 로드
            font = ImageFont.truetype(fontpath, 48)
            # 주어진 이미지(image)를 그리는 객체 생성
            drawing = ImageDraw.Draw(image)
            # 주어진 string(여기서는 character)를 font 스타일로 그렸을 때의 크기(높이, 낮이)를 리턴
            w, h = drawing.textsize(character, font=font)
            # 그릴 글자의 상단 왼쪽 코너의 위치, 그릴 글자, 글자를 채울 색, 폰트 스타일을 지정하여 그림
            # image에 생성됨
            drawing.text(
                ((IMAGE_WIDTH-w)/2, (IMAGE_HEIGHT-h)/2),
                character,
                fill=(255),
                font=font
            )

            # 생성한 글자 이미지를 array 타입으로 변경하여
            # 유니코드 테이블 상으로는 존재하나, 폰트 글자가 존재하지 않는 경우 확인
            # 존재하지 않는 경우 이미지를 생성하지 않고 다음으로 넘어감
            image_arr = numpy.array(image)
            if is_not_existing(image_arr, character):
                continue

            # 현재까지 출력한 이미지의 수를 하나 추가함
            total_count += 1
            current_count += 1
            # 각 폰트의 글자 이미지 file 이름 생성
            file_string = 'hangul_{}.jpeg'.format(total_count)
            # 글자 이미지 path 지정
            file_path = os.path.join(image_dir, file_string)
            # JPEG 형식으로 글자 이미지 생성
            image.save(file_path, 'JPEG')
            # csv 파일에 생성한 글자 이미지와 해당 글자(label)를 나란히 파일에 작성
            labels_csv.write(u'{},{}\n'.format(file_path, character))

        print('Now generating {} images.'.format(current_count))

    print('Finished generating {} images.'.format(total_count))
    labels_csv.close()


def is_not_existing(image, character):
    """
    Check the image whether this is a blank image or not
    공백이 아닌 캐릭터의 출력 이미지가 공백인지 확인

    :param image: numpy.ndarray, image array
    :param character: char, character
    :return: boolean
    """

    if character == " ":  # 해당 글자가 공백이면 아무것도 출력되지 않는 것이 맞으므로 False 리턴
        return False
    else:  # 아무것도 출력되지 않는 빈 공백 이미지인지 확인 후 리턴
        if 255 in image:
            return False

        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--font-dir', type=str, dest='fonts_dir',
                        default=DEFAULT_FONTS_DIR,
                        help='Directory of ttf fonts to use.')
    parser.add_argument('--output-dir', type=str, dest='output_dir',
                        default=DEFAULT_OUTPUT_DIR,
                        help='Output directory to store generated images and '
                             'label CSV file.')
    args = parser.parse_args()

    generate_hangul_images(args.fonts_dir, args.output_dir)

