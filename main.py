import os
import time
import argparse
import numpy as np
import cv2


class FileReader:
    
    @staticmethod
    def read(f_name):
        if os.path.isfile(f_name):
            with open(f_name) as f:
                text = f.read()
        else:
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            if len(files) > 1:
                f_name = files[-1]
                with open(f_name) as f:
                    text = f.read()
            else:
                text = '... ... ... Нажмите <ПРОБЕЛ> для паузы, <ESC> или <q> для выхода. '+\
                        'Для управления скоростью используйте стрелки "вверх" или "вниз". '+\
                        'Вернутся на восемь слов назад - стрелку "влево", прыгнуть на шесть слов вперед '+\
                        '- стрелку "вправо". Приятного чтения! '
                print(f"File is not exist. Please, check the path to file!")
        return text


class Viewer:
    
    def __init__(self, height, weight, bg_color, rectangle_color, line_color):
        self.background = np.zeros((height,weight,3), np.uint8)
        self.background = self.background[::] + bg_color
        self.rectangle = Rectangle(height, weight, rectangle_color)
        self.line1 = Line(self.rectangle, 'h', line_color) 
        self.line2 = Line(self.rectangle, 'v', line_color)
        self.line3 = Line(self.rectangle, 'h2', line_color)
        self.line4 = Line(self.rectangle, 'v2', line_color)
        self.draw(self.rectangle)
        self.draw(self.line1)
        self.draw(self.line2)
        self.draw(self.line3)
        self.draw(self.line4)
        
        self.red_point = int(weight/3)
        self.x_text_position = self.red_point
        self.y_text_position = int(height*3/4) - 60
        
    def draw(self, figure):
        if isinstance(figure, Rectangle):
            cv2.rectangle(self.background,figure.lxly,figure.rxry,figure.color,-1)
        elif isinstance(figure, Line):
            cv2.line(self.background,figure.start_xy,figure.end_xy,figure.color,5)
    
    def get_x_position(self, word_width, letter_width):
        if word_width == letter_width:
            otstup = int(letter_width/2)
        else:
            otstup = word_width - int(letter_width/2)
        return self.red_point - otstup + 1,  self.red_point - int(letter_width/2)
        

    def put_text(self, img, word):
        l = len(word)
        if l >=5:
            prefix = word[:4]
            third_letter = prefix[-1]
        elif l == 4:
            prefix = word[:3]
            third_letter = prefix[-1]
        else:
            prefix = word
            third_letter = prefix[-1]
        letter_width, letter_height = cv2.getTextSize(third_letter, Font.FONT, Font.FONT_SCALE, Font.FONT_THICKNESS)[0]
        
        word_width, word_height = cv2.getTextSize(prefix, Font.FONT, Font.FONT_SCALE, Font.FONT_THICKNESS)[0]
        x_positions = self.get_x_position(word_width, letter_width)
        cv2.putText(img,word,(x_positions[0],self.y_text_position),
                    Font.FONT,Font.FONT_SCALE,(0,0,0),Font.FONT_THICKNESS,cv2.LINE_AA )
        cv2.putText(img,third_letter,(x_positions[1],self.y_text_position),
                    Font.FONT,Font.FONT_SCALE,(10,10,220),Font.FONT_THICKNESS,cv2.LINE_AA )

class Rectangle:
    
    def __init__(self, height, weight, rectangle_color = 220):
        self.color = [rectangle_color] * 3
        self.color = tuple(self.color)
        self.lxly = (0, int(height/4))
        self.rxry = (weight, int(height*3/4))

class Line:
    
    def __init__(self, rectangle, direction : str = 'h', line_color = 97):
        self.color = [line_color] * 3
        self.color = tuple(self.color)
        self.pad_y = 50
        self.pad_x = 20
        if direction == 'h':
            self.horizontal_line_up(rectangle)
        elif direction == 'h2':
            self.horizontal_line_down(rectangle)
        elif direction == 'v':
            self.vertical_line_up(rectangle)
        else:
            self.vertical_line_down(rectangle)
        
    def horizontal_line_up(self, rec):
        self.start_xy = (rec.lxly[0] + self.pad_x, rec.lxly[1] + self.pad_y)
        self.end_xy = (rec.rxry[0] - self.pad_x, rec.lxly[1] + self.pad_y)
    
    def horizontal_line_down(self, rec):
        self.start_xy = (rec.lxly[0] + self.pad_x, rec.rxry[1] - self.pad_y  + 30)
        self.end_xy = (rec.rxry[0] - self.pad_x, rec.rxry[1] - self.pad_y  + 30)
    
    def vertical_line_down(self, rec):
        self.start_xy = (int(rec.rxry[0]/3), rec.rxry[1] - self.pad_y + 10)
        self.end_xy = (int(rec.rxry[0]/3), rec.rxry[1] - self.pad_y  + 30)
    
    def vertical_line_up(self, rec):
        self.start_xy = (int(rec.rxry[0]/3), rec.lxly[1] + self.pad_y + 5)
        self.end_xy = (int(rec.rxry[0]/3), rec.lxly[1] + self.pad_y + 40)

class Font:
    FONT = cv2.FONT_HERSHEY_COMPLEX # cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 1.5
    FONT_THICKNESS = 2

class TextReader:
    
    def __init__(self, text:str, wps):
        self.item = 0
        text = '... ... ... ' + text
        self.text_list= text.split()
        self.wps = wps
        self.delay = 60/self.wps
        self.delay_symbol = ['.', '!', '?', ';']
    
    def set_wps(self, delta):
        self.wps += delta
        self.delay = max(0, 60/self.wps)
    
    def __getitem__(self, item):
        word = self.text_list[item]
        previous_word = self.text_list[item-1]
        delay = self.delay
        if item == 0:
            delay = delay * 2
        if previous_word[-1] in self.delay_symbol:
            delay = delay * 5
        #if abs(self.item - item) > 2:
        #    delay = delay * 3
        self.item = item
        return delay, word
   

def main_loop(text, bg, viewer):
    item = 0
    while True:
        try:
            delay, word = text[item]
        except IndexError:
            break
        img = bg.copy()
        viewer.put_text(img, word)
        cv2.putText(img,str(text.wps),(20,90),
                    Font.FONT,Font.FONT_SCALE,(220,220,220),Font.FONT_THICKNESS-1,cv2.LINE_AA )
        
        key = cv2.waitKey(2)
        time.sleep(delay)
        if key == 81: #ord('<-'):
            item = max(0, item-9)
            cv2.putText(img,' <<<',(200,90),
                        Font.FONT,Font.FONT_SCALE,(10,10,220),Font.FONT_THICKNESS,cv2.LINE_AA )
        elif key == 83: # ord('->'):
            item += 5
            cv2.putText(img,' >>>',(200,90),
                        Font.FONT,Font.FONT_SCALE,(10,10,220),Font.FONT_THICKNESS,cv2.LINE_AA )
        elif key == 82: # upArrow
            #Read Faster
            cv2.putText(img,str(text.wps),(20,90),
                    Font.FONT,Font.FONT_SCALE,(10,10,220),Font.FONT_THICKNESS-1,cv2.LINE_AA )
            text.set_wps(20)
        elif key == 84: # downArrow
            #Read Slower
            cv2.putText(img,str(text.wps),(20,90),
                    Font.FONT,Font.FONT_SCALE,(10,220,10),Font.FONT_THICKNESS-1,cv2.LINE_AA )
            text.set_wps(-20)
        elif key == 32: # ord('SPACE'):
            cv2.putText(img,'PAUSE ',(200,90),
                        Font.FONT,Font.FONT_SCALE,(10,10,220),Font.FONT_THICKNESS,cv2.LINE_AA )
            cv2.imshow('SpeedRead', img)
            while True:
                pause = cv2.waitKey(3)
                if pause == 32:
                    break
        elif key == 27 or key == ord('q'): # 27 = ord('ESC'):
            break
        item += 1
        cv2.imshow('SpeedRead', img)
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str,
                        help="specify the file name")
    args = parser.parse_args()
    file_name = args.file
    text = FileReader.read(file_name)
            
    height_window = 380
    weight_window = 850
    bg_color = 137 # or (137,137,137)
    rectangle_color = 220 # or (220,220,220)
    line_color = bg_color #97 # or (97, 97, 97)
    viewer = Viewer(height_window, weight_window, bg_color, rectangle_color, line_color)
    bg = viewer.background
    start_wps = 200 # fps like
    text = TextReader(text, start_wps)
    main_loop(text, bg, viewer)
    
if __name__ == "__main__":
    main()
    
