import pygame as pg
import random
import sys

# Center_Yを設定し, 球がすべて落ちきったらyを0の位置に設定し直す written by c0a21099
def center_Y(b_rct):
    b_rct.centery = 0


# bombsをglobal変数として利用(のちに爆弾の色などの情報を入れたものとして利用)
bombs = []

# スクリーンの設定
class Screen:
    def __init__(self, title, wh, file):
        pg.display.set_caption(title)
        self.sfc = pg.display.set_mode(wh)
        self.rct = self.sfc.get_rect()
        self.bgi_sfc = pg.image.load(file)
        self.bgi_rct = self.bgi_sfc.get_rect()
    
    def blit(self):
        self.sfc.blit(self.bgi_sfc, self.bgi_rct)


# 操作キャラの設定
class Bird:
    key_delta = {
        pg.K_UP:    [0, -1],
        pg.K_DOWN:  [0, +1],
        pg.K_LEFT:  [-1, 0],
        pg.K_RIGHT: [+1, 0],}

    def __init__(self, fig, rate, xy):
        self.rate = rate
        self.sfc = pg.image.load(fig)
        self.sfc = pg.transform.rotozoom(self.sfc, 0, self.rate)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy
    
    def blit(self, scn):
        scn.sfc.blit(self.sfc, self.rct)

    # 入力キーによって移動 
    def update(self, scr):
        key_dct = pg.key.get_pressed()
        for key, delta in self.key_delta.items():
            if key_dct[key]:
                self.rct.centerx += delta[0]
                self.rct.centery += delta[1]

            if check_bound(self.rct, scr.rct) != (+1, +1):
                self.rct.centerx -= delta[0]
                self.rct.centery -= delta[1]
        self.blit(scr)
    
    # 画像の変更
    def change_image(self, fig):
        self.sfc = pg.image.load(fig)
        self.sfc = pg.transform.rotozoom(self.sfc, 0, self.rate)


# 攻撃の設定 written by c0a21099
class Bomb:
    def __init__(self, col, r, sp, scr):
        self.sfc = pg.Surface((r*2, r*2))
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, col, (r, r), r)
        self.rct = self.sfc.get_rect()
        # centerX = 200(ウィンドウサイズの1/3に設定) written by c0a21099
        self.rct.centerx = random.randint(0, scr.rct.width)
        # centerY = 0(ウィンドウの一番上に設定) written by c0a21099
        center_Y(self.rct)
        self.vx = sp[0]
        self.vy = sp[1]
    
    def blit(self, scr):
        scr.sfc.blit(self.sfc, self.rct)
    
    def update(self, scr):
        self.rct.move_ip(self.vx, self.vy)
        self.blit(scr)

    def stop(self, scr):
        self.vx = 0
        self.vy = 0
        self.rct.centerx = scr.rct.width + 50
        self.rct.centery = scr.rct.height + 50
        self.blit(scr)


# 跳ね返りの確認
def check_bound(obj_rct, scr_rct):
    yoko, tate = +1, +1
    if obj_rct.left < scr_rct.left or scr_rct.right < obj_rct.right:
        yoko = -1
    if obj_rct.top < scr_rct.top + 400 or scr_rct.bottom < obj_rct.bottom:
        tate = -1
    return yoko, tate


def main():
    global bombs
    clock =pg.time.Clock()
    # スクリーンの表示
    SR = Screen("dangerous_kokaton", (600, 900), "fig/bg.png")
    gd_sfc = pg.image.load("fig/gd.png")
    gd_rct = gd_sfc.get_rect()
    gd_rct.center = SR.rct.right/2, SR.rct.bottom-250

    # 操作キャラ、剣表示
    tori = Bird("fig/6.png", 2.0, (200, 600))
    tori.update(SR)

    #爆弾の色設定、進行方向の設定、表示
    colors = ["Red", "Blue", "Green", "Yellow", "Purple"]
    num = 5
    
    # 移動距離の設定 written by c0a21099
    lx = 0
    ly = 1

    for i in range(num):
        # 1ずつ爆弾を画面下部に進める written by c0a21099
        if i == num:
            break
        ly += 1
        color = colors[i % 5]
        bombs.append(Bomb(color, 10, (lx, ly), SR))
        bombs[i].update(SR)

    while True:
        SR.blit()
        SR.sfc.blit(gd_sfc, gd_rct)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        
        # 操作キャラ・剣の位置更新
        tori.update(SR)

        # 陸上・空中によって画像変更
        if (tori.rct.centery < 450):
            tori.change_image("fig/3.png")
        elif (tori.rct.centery >= 450):
            tori.change_image("fig/5.png")

        # ゲームオーバーの設定
        for bomb in bombs:
            bomb.update(SR)
            if tori.rct.colliderect(bomb.rct):
                SR.blit()
                tori.change_image("fig/10.png")
                tori.update(SR)
                pg.display.update()

                clock.tick(0.5)
                return

        # center_yを呼び直して, center_Yの位置をウィンドウの上(y=0)に設定し直し,
        # もう一度玉が落ちるようにする. written by c0a21099
        center_Y(bomb.rct)

        pg.display.update()
        clock.tick(1000)
        

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()