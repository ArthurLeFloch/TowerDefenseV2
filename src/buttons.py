import pygame
from pygame.locals import *

from logs import Logs

def printf(args):
    Logs.print('buttons',args)

def get_image(size, place):
    tmp = pygame.transform.scale(pygame.image.load(place), size).convert_alpha()
    tmp.set_colorkey((255, 255, 255))
    return tmp

class Button:
    
    FONT = None
    BOLD_FONT = None
    
    dict = {}
    
    def __init__(self, name, pos=(100, 100), size=(300, 40), text='Bouton', hoverable = True, thickness = 3, locked = False, font_type=1, need_confirmation=False):
        self.pos = pos
        self.name = name
        self.size = size
        self.thickness = thickness
        self.current_text = text
        self.default_text = text
        self.rect = pygame.Rect((pos[0],pos[1]),(size[0],size[1]))
        self.down = False
        self.im_dict = self.setup()
        self.clickedUp = False
        self.hoverable = hoverable
        self.locked = locked
        self.hovered = False
        self.font_type = font_type
        self.font = self.adapted_font()
        self.need_confirmation = need_confirmation
        self.confirmed = False
        Button.dict[name] = self
    
    def __repr__(self):
        return self.name + ' ' + str(self.down) + ' ' + str(self.clickedUp)
    
    def setup(self):
        locked = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(locked, (60, 60, 60), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(locked, (10, 14, 17), (self.thickness, self.thickness,self.size[0]-2*self.thickness, self.size[1]-2*self.thickness),border_radius=8)
        
        down = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(down, (0, 93, 67), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(down, (0, 66, 47), (self.thickness, self.thickness,self.size[0]-2*self.thickness, self.size[1]-2*self.thickness),border_radius=8)
        
        hovered = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(hovered, (93, 67, 0), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(hovered, (66, 47, 0), (self.thickness, self.thickness,self.size[0]-2*self.thickness, self.size[1]-2*self.thickness),border_radius=8)
        
        classic = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(classic, (90, 90, 90), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(classic, (60, 60, 60), (self.thickness, self.thickness,self.size[0]-2*self.thickness, self.size[1]-2*self.thickness),border_radius=8)

        locked = locked.convert_alpha()
        down = down.convert_alpha()
        hovered = hovered.convert_alpha()
        classic = classic.convert_alpha()
        return {'locked':locked, 'down':down, 'hovered':hovered, 'classic':classic}
    
    def adapted_font(self):
        if self.font_type == 1:
            return Button.FONT
        return Button.BOLD_FONT
    
    def set_text(self, new_text):
        self.default_text = new_text
        self.current_text = new_text
    
    def update(window, x, y, pressed, clicked_up):
        for key in Button.dict:
            self = Button.dict[key]

            if not self.need_confirmation:
                self.clickedUp = False
            self.hovered = False

            hovered = self.rect.collidepoint(x,y)

            if pressed and not hovered:
                self.clickedUp = False
                self.confirmed = False
                if self.need_confirmation:
                    self.current_text = self.default_text

            if pressed and hovered:
                if self.clickedUp:
                    self.confirmed = True
                elif self.need_confirmation:
                    self.current_text = "Confirmer ?"
            self.hovered = hovered
            self.down = hovered and (pressed or clicked_up)
            
            if clicked_up and self.down and not self.locked:
                if self.clickedUp and self.need_confirmation:
                    self.confirmed = True
                self.clickedUp = True
            
            if self.locked:
                window.blit(self.im_dict['locked'], (self.pos[0], self.pos[1]))
            elif self.down or (self.need_confirmation and self.clickedUp):
                window.blit(self.im_dict['down'], (self.pos[0], self.pos[1]))
            elif hovered and self.hoverable:
                window.blit(self.im_dict['hovered'], (self.pos[0], self.pos[1]))
            else:
                window.blit(self.im_dict['classic'], (self.pos[0], self.pos[1]))
            
            if self.locked:
                text = self.font.render(self.current_text, (70, 70, 70))
            else:
                text = self.font.render(self.current_text, (255, 255, 255))
            
            window.blit(text[0], (self.pos[0]+self.size[0]//2-text[1].width//2, self.pos[1]+self.size[1]//2-text[1].height//2))
    
    def delete(*names):
        current_keys = Button.dict.keys()
        for name in names:
            if name in current_keys:
                del Button.dict[name]
    
    def delete_all():
        Button.dict = {}
    
    def exists(name):
        return (name in Button.dict.keys())
    
    def ex_and_clicked(name):
        return Button.exists(name) and Button.dict[name].clickedUp
    
    def ex_and_confirmed(name):
        return Button.exists(name) and Button.dict[name].confirmed
    
    def ex_and_hovered(name):
        return Button.exists(name) and Button.dict[name].hovered
    
    def clicked(name):
        return Button.dict[name].clickedUp
    
    def confirmed(name):
        return Button.dict[name].confirmed
    
    def lock(name):
        Button.dict[name].locked = True
    
    def unlock(name):
        Button.dict[name].locked = False
    
    def set_lock(name, val):
        Button.dict[name].locked = val

class ImageButton:
    dict = {}
    
    def __init__(self, name, image_path, pos=(100, 100), size=(50, 50), hoverable = True, thickness = 3, extern_thickness=1, intern_thickness=2, locked = False):
        self.pos = pos
        self.name = name
        self.size = size
        self.im_size = (size[0]-2*thickness - 2*intern_thickness - 2*extern_thickness, size[1]-2*thickness - 2*intern_thickness -2*extern_thickness)
        self.mask_size = (size[0]-2*thickness-2*extern_thickness, size[1]-2*thickness-2*extern_thickness)
        self.image = get_image(self.im_size, image_path)
        self.intern_thickness = intern_thickness
        self.extern_thickness = extern_thickness
        self.thickness = thickness
        self.rect = pygame.Rect((pos[0],pos[1]),(size[0],size[1]))
        self.down = False
        self.im_dict = self.setup()
        self.clickedUp = False
        self.hoverable = hoverable
        self.locked = locked
        self.hovered = False
        ImageButton.dict[name] = self

    # ! CONVERT ALPHA IMAGES
    def setup(self):
        locked = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(locked, (60, 60, 60), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(locked, (10, 14, 17), (self.thickness, self.thickness, self.size[0] - 2*self.thickness, self.size[1] -2*self.thickness),border_radius=8)
        locked.blit(self.image, (self.thickness + self.intern_thickness + self.extern_thickness, self.thickness + self.intern_thickness + self.extern_thickness))
        mask = pygame.Surface(self.mask_size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (10, 14, 17, 120), (0, 0, *self.mask_size),border_radius=8)
        locked.blit(mask, (self.thickness + self.extern_thickness, self.thickness + self.extern_thickness))

        down = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(down, (0, 93, 67), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(down, (0, 66, 47), (self.thickness, self.thickness, self.size[0] - 2*self.thickness, self.size[1] -2*self.thickness),border_radius=8)
        down.blit(self.image, (self.thickness + self.intern_thickness + self.extern_thickness, self.thickness + self.intern_thickness + self.extern_thickness))
        mask = pygame.Surface(self.mask_size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 40), (0, 0, *self.mask_size),border_radius=8)
        down.blit(mask, (self.thickness + self.extern_thickness, self.thickness + self.extern_thickness))

        hovered = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(hovered, (93, 67, 0), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(hovered, (66, 47, 0), (self.thickness, self.thickness, self.size[0] - 2*self.thickness, self.size[1] -2*self.thickness),border_radius=8)
        hovered.blit(self.image, (self.thickness + self.intern_thickness + self.extern_thickness, self.thickness + self.intern_thickness + self.extern_thickness))
        mask = pygame.Surface(self.mask_size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 20), (0, 0, *self.mask_size),border_radius=8)
        hovered.blit(mask, (self.thickness + self.extern_thickness, self.thickness + self.extern_thickness))

        classic = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(classic, (90, 90, 90), (0, 0, self.size[0], self.size[1]),border_radius=10)
        pygame.draw.rect(classic, (60, 60, 60), (self.thickness, self.thickness, self.size[0] - 2*self.thickness, self.size[1] -2*self.thickness),border_radius=8)
        classic.blit(self.image, (self.thickness + self.intern_thickness + self.extern_thickness, self.thickness + self.intern_thickness + self.extern_thickness))

        locked = locked.convert_alpha()
        down = down.convert_alpha()
        hovered = hovered.convert_alpha()
        classic = classic.convert_alpha()
        return {'locked':locked, 'down':down, 'hovered':hovered, 'classic':classic}

    def delete(*names):
        current_keys = ImageButton.dict.keys()
        for name in names:
            if name in current_keys:
                del ImageButton.dict[name]
    
    def delete_all():
        ImageButton.dict = {}
    
    def exists(name):
        return (name in ImageButton.dict.keys())
    
    def update(window, x, y, pressed, clicked_up):
        for key in ImageButton.dict:
            self = ImageButton.dict[key]

            self.clickedUp = False
            self.hovered = False

            hovered = self.rect.collidepoint(x,y)

            if pressed and not hovered:
                self.clickedUp = False
                self.confirmed = False
            
            self.hovered = hovered
            self.down = hovered and (pressed or clicked_up)
            
            if clicked_up and self.down and not self.locked:
                self.clickedUp = True
            
            if self.locked:
                window.blit(self.im_dict['locked'], (self.pos[0], self.pos[1]))
            elif self.down:
                window.blit(self.im_dict['down'], (self.pos[0], self.pos[1]))
            elif hovered and self.hoverable:
                window.blit(self.im_dict['hovered'], (self.pos[0], self.pos[1]))
            else:
                window.blit(self.im_dict['classic'], (self.pos[0], self.pos[1]))
    
    def ex_and_clicked(name):
        return ImageButton.exists(name) and ImageButton.dict[name].clickedUp
    
    def ex_and_confirmed(name):
        return ImageButton.exists(name) and ImageButton.dict[name].confirmed
    
    def ex_and_hovered(name):
        return ImageButton.exists(name) and ImageButton.dict[name].hovered
    
    def clicked(name):
        return ImageButton.dict[name].clickedUp

    def set_lock(name, lock):
        ImageButton.dict[name].locked = lock
    
    def set_pos(name, pos):
        self = ImageButton.dict[name]
        self.pos = pos
        self.rect = pygame.Rect((pos[0], pos[1]), (self.size[0], self.size[1]))

    def lock(name):
        ImageButton.dict[name].locked = True
    
    def unlock(name):
        ImageButton.dict[name].locked = False
    
    def set_lock(name, val):
        ImageButton.dict[name].locked = val