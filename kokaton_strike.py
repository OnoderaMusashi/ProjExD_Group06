import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 500
HEIGHT = 700
DECELERATION_RATE = 0.96  # 減速率
os.chdir(os.path.dirname(os.path.abspath(__file__)))



class ReflectiveDiffuserBullet(pg.sprite.Sprite):
    """
    友情コンボ　反射拡散弾を描画する
    """
    def __init__(self, pos: tuple[int, int]) -> None:
        """
        イニシャライザー
        引数 pos：キャラクターの座標タプル
        戻り値：なし
        """
        super().__init__()
        img = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), 0, 2.0)
        img0 = pg.transform.flip(img, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (1, 0): img,  # 右
            (1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, 1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, 1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (1, 1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.image = img0
        self.dire = [0, 0]
        while self.dire == [0, 0]:
            self.dire = [random.randint(-1, 1), random.randint(-1, 1)]
        self.d = 5
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.attack = 1000  # 友情コンボのダメージ量
        self.life = 3  # 発動時間

    def update(self):
        """
        拡散弾の位置を更新、壁と衝突したら反転、3回反射したらkillする
        """
        self.image = self.imgs[tuple(self.dire)]  # 方向によって画像を切り替える
        self.rect.move_ip(self.dire[0]*self.d, self.dire[1]*self.d)  # キャラクター位置を更新
        if 30 > self.rect.centerx:  # 左壁判定
            self.rect.centerx = 30  # キャラクターを壁の中に戻す
            self.dire[0] *= -1  # ベクトルを反転させる
            self.life -= 1
        if WIDTH-30 < self.rect.centerx:  # 右壁判定
            self.rect.centerx = WIDTH-30
            self.dire[0] *= -1 
            self.life -= 1
        if 30 > self.rect.centery:  # 上壁判定
            self.rect.centery = 30
            self.dire[1] *= -1 
            self.life -= 1
        if HEIGHT-175-30 < self.rect.centery:  # 下壁判定
            self.rect.centery = HEIGHT-175-30
            self.dire[1] *= -1
            self.life -= 1
        if self.life < 0:  # 3回反射したら
            self.kill()


class GameManager:
    """
    ゲームの進行を管理するクラス
    """
    def __init__(self):
        """
        ゲームの状態やターン数を初期化する
        -state-
        initial:初期状態
        wait:待機状態
        drag:引っ張っている状態
        drag_end:引っ張り終えた状態
        move:キャラクターが動いている状態
        end_process:キャラクターが止まり次への処理をしている状態
        """
        self.state = "initial"
        self.turn = 0
        self.characters = []
        self.vec = (0, 0)
        self.speed = 0
        self.hp = 10000
        self.maxhp = 10000
    
    def create(self):
        """
        キャラクターを生成するメソッド
        引数：なし
        戻り値：birdsグループ
        """
        self.birds = pg.sprite.Group()
        for i in range(4):  # キャラクターを4体分生成
            self.characters.append(Bird(i))
            self.birds.add(self.characters[i])  # グループに入れる
            self.maxhp += self.characters[i].hp  # 合計HPを設定
        self.state = "wait"
        self.hp = self.maxhp  # 現在のHPを最大HPに設定
        return self.birds

    def set(self, v):
        """
        手番のモンスターの情報を初期化
        引数1 v：単位化されたベクトル
        """
        self.vec = v  # 単位化したベクトルを設定
        self.speed = self.characters[self.turn%4].speed  # 動き出す前にスピードを保存する
        self.characters[self.turn%4].dx, self.characters[self.turn%4].dy = 1, 1  # ベクトルを反転させるかを決める変数
    
    def update(self, screen, tmr: int):
        if self.state == "move":
            self.characters[self.turn%4].update(self.vec)
            if tmr % 30 == 0:
                self.characters[self.turn%4].speed -= self.speed - self.speed*DECELERATION_RATE
                if self.characters[self.turn%4].speed < 1:
                    self.characters[self.turn%4].speed = 0
                    self.state = "end_process"
        self.birds.draw(screen)
        self.img = pg.Surface((WIDTH, 175))
        pg.draw.rect(self.img, (238, 120, 0), (0, 0, WIDTH, 175))
        for i in range(4):
            if self.turn%4 == i:
                pg.draw.rect(self.img, (255, 255, 0), (10+100*i, 50, 90, 90))
                continue
            pg.draw.rect(self.img, (255, 255, 255), (10+100*i, 50, 90, 90))
        pg.draw.rect(self.img, (128, 128, 128), (75, 15, 400, 20))
        pg.draw.rect(self.img, (154, 205, 50), (77, 17, 396*(self.hp/self.maxhp), 16))

        for i in range(4):
            self.img.blit(self.characters[self.turn%4].imgs[i], (25+100*i, 65))

        self.font1 = pg.font.Font(None, 40)
        self.font2 = pg.font.Font(None, 100)
        self.font3 = pg.font.Font(None, 30)
        self.txt1 = self.font1.render("HP", True, (0, 255, 0))
        self.txt2 = self.font1.render("Turn", True, (255, 255, 255))
        self.txt3 = self.font2.render(str(self.turn+1), True, (255, 255, 255))
        self.t3_rct = self.txt3.get_rect()
        self.t3_rct.center = 450, 110
        self.txt4 = self.font3.render(str(self.hp)+" / "+str(self.maxhp), True, (255, 255, 255))
        self.t4_rct = self.txt4.get_rect()
        self.t4_rct.center = 390, 25

        self.img.blit(self.txt1, (10, 10))
        self.img.blit(self.txt2, (420, 50))
        self.img.blit(self.txt3, self.t3_rct)
        self.img.blit(self.txt4, self.t4_rct)
        screen.blit(self.img, (0, 525))
    
    def end_process(self):
        """
        キャラクターが止まった時に行う処理
        引数：なし
        戻り値：なし
        """
        self.characters[self.turn%4].speed = self.speed
        self.vec = (0, 0)
        self.speed = 0
        self.characters[self.turn%4].dx = 1
        self.characters[self.turn%4].dy = 1
        self.turn += 1
        self.state = "wait"

    def now_character(self, num=None):
        """
        指定したキャラクターをのインスタンスを取得する
        引数 num：三番目のキャラクターか・デフォルトはNone(手番のキャラクター)
        戻り値：指定したキャラクターのインスタンス
        """
        if num is None:
            num = self.turn%4
        return self.characters[num]
    

class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター(こうかとん)に関するクラス
    """
    def __init__(self, num: int):
        """
        こうかとん画像Surfaceを生成する
        当たり判定用の円Surfaceを生成する
        引数1 num：何番目に生成されたキャラクターか
        """
        super().__init__()
        character_dic = {0:[50, 1000, 2500],
                         1:[50, 1000, 2500],
                         2:[50, 1000, 2500],
                         3:[50, 1000, 2500]}  # {key:[スピード, 攻撃力, HP]}
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/1.png"), 0, 1.25)
        img1 = pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 0, 1.25)
        self.imgs = {0:img0, 1:img1,
                2:pg.transform.flip(img0, True, False),
                3:pg.transform.flip(img1, True, False)}
        self.image = self.imgs[num]  # 写真を設定
        self.speed = character_dic[num][0]  # スピードを設定
        self.attack = character_dic[num][1]  # 攻撃力を設定
        self.hp = character_dic[num][2]  # HPを設定
        self.rect = self.image.get_rect()  # rectを取得
        # キャラクターの初期位置をランダムに設定
        self.x, self.y = random.randint(95+100*num, 105+100*num), random.randint(450, 490)
        self.rect.center = (self.x, self.y)  # キャラクターの位置を設定
        self.dx, self.dy = 1, 1  # 反転するかの変数を初期化
        self.bump_combo = True  # 初期状態でbump_comboをTrueに設定


    
    def update(self, v):
        self.rect.move_ip(self.dx*v[0]*self.speed, self.dy*v[1]*self.speed)  # キャラクター位置を更新
        if 30 > self.rect.centerx:  # 左壁判定
            self.rect.centerx = 30  # キャラクターを壁の中に戻す
            self.dx *= -1  # ベクトルを反転させる
        if WIDTH-30 < self.rect.centerx:  # 右壁判定
            self.rect.centerx = WIDTH-30
            self.dx *= -1
        if 30 > self.rect.centery:  # 上壁判定
            self.rect.centery = 30
            self.dy *= -1
        if HEIGHT-175-30 < self.rect.centery:  # 下壁判定
            self.rect.centery = HEIGHT-175-30
            self.dy *= -1


class Arrow:
    """
    矢印を管理するクラス
    """
    def __init__(self, pos):
        """
        イニシャライザー　始点を設定する
        マウスを押したら呼び出される
        引数 pos：引っ張り始めた点の座標
        """
        self.ax, self.ay = pos  # 引っ張り始めた点の座標を設定
    
    def set_b(self, vec: tuple[int, int]):
        """
        マウスを離した時にベクトルを確定し、長さを判定する
        マウスを離したら呼び出られる
        引数 vec：矢印ベクトル
        戻り値：矢印の長さが一定以上かを示すbool値
        """
        self.vx, self.vy = vec[0]*-1, vec[1]*-1  # 矢印ベクトルを確定する
        self.l = math.dist((0, 0), vec)  # 矢印をの長さを確定する
        return True if self.l > 40 else False  # 引っ張った長さが40以下ならFalse, それより大きかったらTrueを返す
    
    def draw_(self ,mouse: tuple[int, int] ,pos: tuple[int, int], screen):
        """
        引っ張っている間に矢印を描画するメソッド
        引数1 mouse：マウスの現在
        引数2 pos：手番のモンスターの現在座標タプル
        引数3 screen：画面Surface
        戻り値：なし
        """
        self.cx, self.cy = mouse  # 現在のマウス座標を設定
        self.x, self.y = pos  # 現在のキャラクターの座標を設定
        self.r = math.degrees(math.atan2(self.cy-self.ay, self.cx-self.ax))*-1  # 左向きの矢印を0として回転角を求める
        self.v = math.dist((self.ax, self.ay), mouse)  # 矢印をの長さを求める
        self.image = pg.Surface((self.v*2, 140))  # 矢印の大きさに合わせたSurfaceを作成
        pg.draw.lines(self.image, (0, 0, 255), True, [(self.v*2, 70),
                                                      (self.v*0.6, 40),
                                                      (self.v*0.8, 5),
                                                      (0, 70),
                                                      (self.v*0.8, 135),
                                                      (self.v*0.6, 100)])  # 矢印を作成
        self.image.set_colorkey((0, 0, 0))
        self.image = pg.transform.rotate(self.image, self.r)  # 回転角の分だけSurfaceごと回転する
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)  # 矢印の中心をキャラクター位置に合わせる
        if self.v > 40:  # 引っ張った長さが40より大きいか？
            screen.blit(self.image, self.rect)
    
    def get_vector(self):
        """
        単位化したベクトル取得するメソッド
        引数：なし
        戻り値：単位化したベクトルのタプル
        """
        self.ux = self.vx/self.l  # X成分を単位化
        self.uy = self.vy/self.l  # Y成分を単位化
        # print("ux:"+str(self.ux)+", uy:"+str(self.uy))
        return self.ux, self.uy  # 単位化したベクトルを返す


def main():
    pg.display.set_caption("こうかとんストライク")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    game = GameManager()  # ゲームを初期化する
    birds = game.create()  # こうかとんグループを生成

    tmr = 0
    reflective_diffuser_bullets = pg.sprite.Group()
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()  # 押されたkey
        mouse_pos = pg.mouse.get_pos()  # マウスの座標
        # event処理
        for event in pg.event.get():
            # ×ボタンをクリックした時
            if event.type == pg.QUIT:
                return
            # keyを押した時(1回のみ)
            if event.type == pg.KEYDOWN:
                print("keyを押した")
            # keyを離した時(1回のみ)
            if event.type == pg.KEYUP:
                pass
            # マウスボタンを押した時(1回のみ)
            if event.type == pg.MOUSEBUTTONDOWN:
                # 待機状態の時
                if game.state == "wait":
                    game.state = "drag"
                    pg.mouse.get_rel()  # マウスの移動距離を0にする
                    arrow = Arrow(mouse_pos)  # 矢印クラスのインスタンス生成
            # マウスボタンを離した時(1回のみ)
            if event.type == pg.MOUSEBUTTONUP:
                if game.state == "drag":
                    game.state = "drag_end"
                    if arrow.set_b(pg.mouse.get_rel()):  # 引っ張り終えた座標を確定
                        # 矢印の長さが40より大きいなら
                        game.state = "move"
                        game.set(arrow.get_vector())  # 単位化したベクトルを引数に手番のキャラクターの情報を設定する
                    else:
                        # 矢印の長さが40以下なら
                        game.state = "wait"
        for mouse_pressed in pg.mouse.get_pressed():
            if mouse_pressed:
                # マウスを押している間
                pass

        # 画面処理
        screen.blit(bg_img,[0,0])  # 背景を描画する
        if game.state == "move":  # 手番のキャラクターが動いているとき(敵にダメージを与えられるとき)
            # 手番のキャラクターと2のキャラクターとの衝突判定
            if game.now_character().rect.colliderect(game.now_character(2).rect) and game.now_character(2).bump_combo:
                if game.turn%4 != 2:
                    for i in range(10):
                        reflective_diffuser_bullets.add(ReflectiveDiffuserBullet(game.now_character(2).rect.center))
                    game.now_character(2).bump_combo = False
        reflective_diffuser_bullets.update()
        reflective_diffuser_bullets.draw(screen)

        game.update(screen, tmr)  # ゲーム進行を更新する
        if game.state == "drag":  # 矢印を引っ張ている間
            arrow.draw_(mouse_pos, game.now_character().rect.center, screen)  # 矢印を描画

        # 更新処理
        if game.state == "end_process":
            game.end_process()  # ターンの最終処理をする
        pg.display.update()
        tmr += 1
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()