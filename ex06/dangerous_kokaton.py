import pygame as pg
import random
import sys
import time

# ゲーム状態の判断(タイトル/ゲーム画面の推移に使用) written by c0a21099
TITLE, STAGE = range(2)
game_state = TITLE


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
    

# 背景の設定
class BackGround:
    def __init__(self, file, xy):
        self.sfc = pg.image.load(file)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy
    def blit(self, scn):
        scn.sfc.blit(self.sfc, self.rct)


# 操作キャラの設定
class Bird:

    key_delta = {
        pg.K_UP:    [0, -2],
        pg.K_DOWN:  [0, +2],
        pg.K_LEFT:  [-2, 0],
        pg.K_RIGHT: [+2, 0],
        pg.K_w:     [0, -2],
        pg.K_s:     [0, +2],
        pg.K_a:     [-2, 0],
        pg.K_d:     [+2, 0]
        }

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
        global move, out_fin #移動許可、終了条件の変更 c0a21049
        key_dct = pg.key.get_pressed()
        for key, delta in self.key_delta.items():
            if move:#移動許可があれば C0A21049
                if key_dct[key]:
                    self.rct.centerx += delta[0]
                    self.rct.centery += delta[1]

                if check_bound(self.rct, scr.rct) != (+1, +1):
                    out_fin = True#場外に出たので終了する c0a21049
            else:#移動許可がない時リスタートする c0a21049
                if key_dct[pg.K_r]:
                    move = True
                    out_fin = False#場外判定を消す c0a21049
                    main()
                elif key_dct[pg.K_e]:
                    sys.exit()
        self.blit(scr)

        #マウスカーソル C0A21089
        for event in pg.event.get():
            if move:
                if event.type == pg.MOUSEMOTION:   #もしイベントタイプががMOUSEMOTIONなら
                    x, y = event.pos
                    if (scr.rct.left < x < scr.rct.right) and (scr.rct.bottom - 500 <  y < scr.rct.bottom):
                        self.rct.centerx, self.rct.centery = x, y #tori.rct.centerx,tori.rct.centeryにマウスカーソルの座標を取得  

    # 画像の変更
    def change_image(self, fig):
        self.sfc = pg.image.load(fig)
        self.sfc = pg.transform.rotozoom(self.sfc, 0, self.rate)


# 爆弾の設定
class Bomb:
    def __init__(self, col, r, sp, scr):
        self.sfc = pg.Surface((r*2, r*2))
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, col, (r, r), r)
        self.rct = self.sfc.get_rect()
        pos = random.randint(0, 3)  #爆弾の飛んでくる方向(左,上,右,下)
        rad_x = random.randint(0, scr.rct.width)
        rad_y = random.randint(scr.rct.height-500, scr.rct.height)
        bombx = [10, rad_x, scr.rct.width-10, rad_x]    #飛んでくる方向によって
        bomby = [rad_y, 410, rad_y, scr.rct.height-10]  #爆弾の進む向き、初期位置を設定
        vx = [1, sp[0], -1, sp[0]]
        vy = [sp[1], 1, sp[1], -1]
        self.rct.centerx = bombx[pos]
        self.rct.centery = bomby[pos]
        self.vx = vx[pos]
        self.vy = vy[pos]
    
    def blit(self, scr):
        scr.sfc.blit(self.sfc, self.rct)
    
    #爆弾の移動
    def update(self, scr, bmlist):
        if move:
            self.rct.move_ip(self.vx, self.vy)
        yoko, tate = check_bound(self.rct, scr.rct)
        #爆弾が端に到達したとき C0A21035
        if (yoko == -1) or (tate == -1):
            self.restart(scr)
        self.blit(scr)

    #爆弾の位置の再設定 C0A21035
    def restart(self, scr):
        pos = random.randint(0, 3)
        x = random.choice([-1, 1])
        y = random.choice([-1, 1])
        rad_x = random.randint(0, scr.rct.width)
        rad_y = random.randint(scr.rct.height-500, scr.rct.height)
        bombx = [10, rad_x, scr.rct.width-10, rad_x]
        bomby = [rad_y, 410, rad_y, scr.rct.height-10]
        vx = [1, x, -1, x]
        vy = [y, 1, y, -1]
        self.rct.centerx = bombx[pos]
        self.rct.centery = bomby[pos]
        self.vx = vx[pos]
        self.vy = vy[pos]


#行動可能領域から出たときの判定(一部修正) C0A21035
def check_bound(obj_rct, scr_rct):
    yoko, tate = +1, +1
    if obj_rct.left < scr_rct.left or scr_rct.right < obj_rct.right:
        yoko = -1
    if obj_rct.top < scr_rct.bottom - 500 or scr_rct.bottom < obj_rct.bottom:
        tate = -1
    return yoko, tate


#バリアの設定 C0A21035
class Protecter:

    key_delta = {
        pg.K_UP:    [0, -1],
        pg.K_DOWN:  [0, +1],
        pg.K_LEFT:  [-1, 0],
        pg.K_RIGHT: [+1, 0],}

    def __init__(self, rate, bird):
        self.rate = rate
        self.sfc = pg.image.load("fig/barrior.png")
        self.sfc = pg.transform.rotozoom(self.sfc, 0, self.rate)
        self.rct = self.sfc.get_rect()
        self.rct.center = bird.rct.centerx, bird.rct.centery
        self.count = 3
    
    def blit(self, scn):
        scn.sfc.blit(self.sfc, self.rct)

    #操作キャラに合わせたバリアの移動
    def update(self, scr, tori):
        if self.count <= 0:
            self.delete(scr)
            return
        self.rct.centerx = tori.rct.centerx
        self.rct.centery = tori.rct.centery
        self.blit(scr)
    
    #画面上からバリアを消去
    def delete(self, scr):
        self.rct.centerx = 2000
        self.rct.centery = 2000


# テキストの設定 (Press space で使用) written by c0a21099
def text(scr, fnt, size, wrd, col, xy):
    fonto = pg.font.Font(fnt, size)
    txt = fonto.render(wrd, True, col)
    scr.sfc.blit(txt, xy)


#経過時間を表示  c0a21121
def timer(scr, jikan):
    text(scr, None, 80, f"{jikan:.1f} sec", 0, (240,20))


#ゲームスコアを表示 c0a21121
def score(scr, jikan):
    jikan *= 100
    text(scr, None, 120, f"{jikan:.0f} Points", (0,100,0), (100,300))


def main():
    global move#移動許可、終了条件の変更 c0a21049
    global game_state
    clock = pg.time.Clock()
    # スクリーンの表示
    SR = Screen("戦え！こうかとん", (600, 900), "fig/bg.png")
    GD = BackGround("fig/gd.png", (SR.rct.right/2, SR.rct.bottom-250))

    # 操作キャラ表示
    tori = Bird("fig/6.png", 1.0, (200, 600))
    tori.update(SR)

    # バリア表示 C0A21035
    prot = Protecter(1.0, tori)
    prot.update(SR, tori)

    # 爆弾設定・表示
    bombs = []
    num = 20
    for i in range(num):
        vx = random.choice([-1, 1])
        vy = random.choice([-1, 1])
        bombs.append(Bomb("blue", 5, (vx, vy), SR))
        bombs[i].update(SR, bombs)

    # title画面の画像
    logo = BackGround("fig/logo.png", (300, 300))

    st = time.time()

    while True:
        SR.blit()
        GD.blit(SR)
        if move:
            now = pg.time.get_ticks()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # ゲーム状態の判断 written by c0a21099
        if game_state == TITLE:
            SR.blit()
            GD.blit(SR)
            # タイトルロゴの追加
            logo.blit(SR)
            start_txt = text(SR, None, 100, "Press SPACE", "WHITE", (75, 600))
            pg.display.update()

            for event in pg.event.get(): 
                if event.type == pg.KEYUP:  # キーを押したとき
                    # spaceを押したらgame_stateをSTAGEにし, ゲームを開始する
                    if event.key == pg.K_SPACE:
                        game_state = STAGE
                        st = time.time()
        
        elif game_state == STAGE:
            # 操作キャラの位置更新
            tori.update(SR)
            prot.update(SR, tori)

            for bomb in bombs:
                bomb.update(SR, bombs)
                if prot.rct.colliderect(bomb.rct):  #バリアと爆弾がぶつかった時 C0A21035
                    bomb.restart(SR)
                    prot.count -= 1
                if tori.rct.colliderect(bomb.rct) or out_fin == True:
                    SR.blit()
                    GD.blit(SR)
                    tori.change_image("fig/10.png")
                    tori.update(SR)
                    #終了時の経過時間の表示 c0a21121
                    timer(SR, tmr)
                    #終了時のゲームスコアの表示 c0a21121
                    score(SR, tmr)

                    #リスタートを促す文字を表示する C0A21049
                    text(SR, None, 40, "Press the 'r' key and try again!", 0, (100, 500))
                    #ゲーム終了する際のテキストを表示する　C0A21035
                    text(SR, None, 40, "Press the 'e' key and finish", 0, (120, 550))
                    pg.display.update()
                    move = False#移動を許可しない c0a21049

            #時間の表示 c0a21121
            if move:
                ed = time.time()
                tmr = ed-st
            timer(SR, tmr)

            pg.display.update()
            clock.tick(1000)


if __name__ == "__main__":
    pg.init()
    move = True #移動許可 C0A21049
    out_fin = False #場外による終了 c0a21049
    main()
    pg.quit()
    sys.exit()