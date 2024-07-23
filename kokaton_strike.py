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
        # self.state = "wait"
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
                    
    def update(self, screen, tmr: int, f: bool):
        if self.state == "move":
            self.characters[self.turn%4].update(self.vec, screen)
            if tmr % 30 == 0:
                self.characters[self.turn%4].speed -= self.speed - self.speed*DECELERATION_RATE
                if self.characters[self.turn%4].speed < 1:
                    self.characters[self.turn%4].speed = 0
                    if f:
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
            self.img.blit(self.characters[self.turn%4].imgs[i], (15+100*i, 55))

        self.font1 = pg.font.Font(None, 40)
        self.font2 = pg.font.Font(None, 100)
        self.font3 = pg.font.Font(None, 30)
        self.font4 = pg.font.SysFont("hgpｺﾞｼｯｸe", 20)
        self.txt1 = self.font1.render("HP", True, (0, 255, 0))
        self.txt2 = self.font1.render("Turn", True, (255, 255, 255))
        self.txt3 = self.font2.render(str(self.turn+1), True, (255, 255, 255))
        self.t3_rct = self.txt3.get_rect()
        self.t3_rct.center = 450, 110
        self.txt4 = self.font3.render(str(self.hp)+" / "+str(self.maxhp), True, (255, 255, 255))
        self.t4_rct = self.txt4.get_rect()
        self.t4_rct.center = 390, 25
        self.txt5 = self.font4.render("Mキーでリセット画面", True, (0, 0, 255))


        self.img.blit(self.txt1, (10, 10))
        self.img.blit(self.txt2, (420, 50))
        self.img.blit(self.txt3, self.t3_rct)
        self.img.blit(self.txt4, self.t4_rct)
        self.img.blit(self.txt5, (300, 145))
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
        for c in self.characters:
            c.bump_combo = True  # 友情コンボを発動可にする

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
        character_dic = {0:{"speed":50, "attack":1000, "HP":2500, "combo_name":"全属性エナジーサークル", "combo_attack":5000, "name":"ぶっ鳥", "picture":"一石"},
                         1:{"speed":50, "attack":1000, "HP":2500, "combo_name":"十字レーザー", "combo_attack":5000, "name":"カモメ", "picture":"小野寺"},
                         2:{"speed":50, "attack":1000, "HP":2500, "combo_name":"反射拡散弾", "combo_attack":2000, "name":"ガンとん", "picture":"矢田"},
                         3:{"speed":50, "attack":1000, "HP":2500, "combo_name":"ハイエナジーサークル", "combo_attack":500000, "name":"ストークミート", "picture":"原口"}}
                         # {key:{"speed":スピード, "attack":攻撃力, "HP":HP}}
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/tegaki_kokaton.png"), 0, 1.3)
        img1 = pg.transform.rotozoom(pg.image.load(f"fig/kokaton02.png"), 0, 1.25)
        img2 = pg.transform.rotozoom(pg.image.load(f"fig/kessaku_kai.png"), 0, 1.25)
        img3 = pg.transform.rotozoom(pg.image.load(f"fig/kokaton_2.png"), 0, 1.25)
        self.imgs = {0:img0, 1:img1, 2:img2, 3:img3}
        self.image = self.imgs[num]  # 写真を設定
        self.speed = character_dic[num]["speed"]  # スピードを設定
        self.attack = character_dic[num]["attack"]  # 攻撃力を設定
        self.hp = character_dic[num]["HP"]  # HPを設定
        self.rect = self.image.get_rect()  # rectを取得
        # キャラクターの初期位置をランダムに設定
        self.x, self.y = random.randint(95+100*num, 105+100*num), random.randint(450, 490)
        self.rect.center = (self.x, self.y)  # キャラクターの位置を設定
        self.dx, self.dy = 1, 1  # 反転するかの変数を初期化
        self.bump_combo = True  # 友情コンボがこのターンで発動されたかを保存する
        self.bump_combo_name = character_dic[num]["combo_name"]  # 友情コンボの名前を保存
        self.bump_combo_attack = character_dic[num]["combo_attack"]  # 友情コンボのダメージ量を保存
        self.name = character_dic[num]["name"]  # 名前を保存
        self.picture_by = character_dic[num]["picture"]  # 絵の作者
        self.reflections = pg.sprite.Group()  # 反射した時に現れる図形
    
    def update(self, v, screen):
        self.rect.move_ip(self.dx*v[0]*self.speed, self.dy*v[1]*self.speed)  # キャラクター位置を更新
        if 30 > self.rect.centerx:  # 左壁判定
            self.rect.centerx = 30  # キャラクターを壁の中に戻す
            self.dx *= -1  # ベクトルを反転させる
            self.reflections.add(Reflection((self.rect.left+30, self.rect.centery)))
        if WIDTH-30 < self.rect.centerx:  # 右壁判定
            self.rect.centerx = WIDTH-30
            self.dx *= -1
            self.reflections.add(Reflection((self.rect.right-30, self.rect.centery)))
        if 30 > self.rect.centery:  # 上壁判定
            self.rect.centery = 30
            self.dy *= -1
            self.reflections.add(Reflection((self.rect.centerx, self.rect.top+30)))
        if HEIGHT-175-30 < self.rect.centery:  # 下壁判定
            self.rect.centery = HEIGHT-175-30
            self.dy *= -1
            self.reflections.add(Reflection((self.rect.centerx, self.rect.bottom-30)))
        self.reflections.update()
        self.reflections.draw(screen)



class Reflection(pg.sprite.Sprite):
    """
    キャラが壁に反射したときに描画される図形を描くクラス
    """
    def __init__(self, pos: tuple[int, int]) -> None:
        """
        イニシャライザー
        引数 pos：キャラの座標タプル
        """
        super().__init__()
        r1_list = []  # 小さい六角形の座標リスト
        r2_list = []  # 大きい六角形の座標リスト
        for r in range(30, 391, 60):  # 6角形の座標を生成
            r1_list.append(rotate_pos((15, 15), 5, r))
            r2_list.append(rotate_pos((15, 15), 15, r))
        self.image = pg.Surface((32, 32))  # 壁に反射したときに描画される図形を描くSurface
        pg.draw.lines(self.image, (0, 0, 255), True, r1_list, 4)  # 小さい六角形
        pg.draw.lines(self.image, (0, 0, 255), True, r2_list, 4)  # 大きい六角形
        self.image.set_alpha(100)  # 透明度を設定
        self.image.set_colorkey((0, 0, 0))  # 黒を透明にする
        self.rect = self.image.get_rect()
        self.rect = pos
        self.life = 5  # 5フレーム描画する
    
    def update(self):
        """
        lifeが0になったらkillする
        """
        self.life -= 1
        if self.life <= 0:
            self.kill()
        

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
        pg.draw.polygon(self.image, (0, 0, 255), [(self.v*2, 70),
                                                  (self.v*0.6, 40),
                                                  (self.v*0.8, 5),
                                                  (0, 70),
                                                  (self.v*0.8, 135),
                                                  (self.v*0.6, 100)])  # 矢印を作成
        self.image.set_alpha(128)
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


def rotate_pos(center: tuple[int, int], l: int, r: int) -> tuple[int, int]:
    """
    与えられた座標を中心に反時計回りにr°回転した座標を返す
    引数1 center：原点
    引数2 l：半径
    引数3 r：回転角度(度)
    戻り値：回転後の座標タプル
    """
    return l*math.cos(math.radians(r))+center[0], l*math.sin(math.radians(r))+center[1]


class Enemy(pg.sprite.Sprite):
    """
    敵に関するクラス
    """
    def __init__(self, emy: str) -> None:
        """
        イニシャライザー
        引数 emy：描画したい敵の名前
        戻り値：なし
        """
        super().__init__()
        # 敵情報を格納した辞書
        imgs = {"唐揚げ":{"img":pg.transform.rotozoom(pg.image.load(f"fig/karaage.png"), 0, 0.2), "color":"blue"},
                "手羽先":{"img":pg.transform.rotozoom(pg.image.load(f"fig/tebasaki.png"), 0, 0.15), "color":"green"},
                "ローストチキン":{"img":pg.transform.rotozoom(pg.image.load(f"fig/roast_chicken.png"), 0, 1.0), "color":"yellow"}}
        self.image = imgs[emy]["img"]  # 敵画像を設定
        self.color = imgs[emy]["color"]  # HPバーの色を設定
        self.rect = self.image.get_rect()
        self.rect.center = 250, 250  # 中心に設定
        self.hp = 10000000  # HPを設定
        self.maxhp = self.hp  # 最大HPを設定
        self.interval = 3  # 攻撃間隔を設定
        self.turn_maxhp = self.hp  # ターンごとの残りHP最大値を設定

        # 弱点関係
        self.r = 15  # 弱点の大きさを決める変数
        self.v = 0  # 弱点の回転角度を決める変数
        self.weakpoint = pg.Surface((self.r*2, self.r*2))  # 弱点Surfaceを作成
        self.weakpoint_rct = self.weakpoint.get_rect()
        self.weakpoint_rct.center = self.rect.center  # 敵の中心に弱点を設定
    
    def update(self, screen: pg.Surface) -> None:
        """
        HPバー・攻撃間隔・弱点の生成・更新・表示を行う
        引数 screen：画面Surface
        戻り値：なし
        """
        # 敵のHPバーの生成
        self.color_dic = {"blue":(160, 216, 239), "green":(184, 210, 0), "yellow":(255, 255, 0), "gray":(128, 128, 128)}
        self.colors = ["yellow", "green", "blue"]
        self.hpbar = pg.Surface((400, 20))
        pg.draw.rect(self.hpbar, self.color_dic["gray"], (0, 0, 400, 20))  # HPバーの灰色部分を描く
        for color in self.colors[:self.colors.index(self.color)]:
            pg.draw.rect(self.hpbar, self.color_dic[color], (2, 2, 396, 16))
        pg.draw.rect(self.hpbar, (255, 0, 0), (2, 2, 396*(self.turn_maxhp/self.maxhp), 16))  # HPバーの残量を描く
        pg.draw.rect(self.hpbar, self.color_dic[self.color], (2, 2, 396*(self.hp/self.maxhp), 16))  # HPバーの残量を描く
        screen.blit(self.hpbar, [10, 10])  # 画面に描画

        # 攻撃間隔の表示
        font = pg.font.Font(None, 40)  #文字サイズを80に設定
        txt = font.render(str(self.interval+1), True, (255, 0, 0))  # 文字を作成
        txt_rct = txt.get_rect()
        txt_rct.center = self.rect.centery+50, self.rect.centery-60  # 文字の中心を敵右上に設定
        screen.blit(txt, txt_rct)  # 画面に描画

        txt2 = font.render("BOSS", True, (167, 87, 168))  # 文字を作成
        txt_rct2 = txt2.get_rect()
        txt_rct2.center = 453, 20  # 文字の中心を敵右上に設定
        screen.blit(txt2, txt_rct2)  # 画面に描画

        # 弱点の生成
        self.weakpoint.fill((0, 0, 0))  # Surfaceを黒で更新
        # 時計回りに回る空色の正三角形
        pg.draw.lines(self.weakpoint, (157, 204, 224), True, [rotate_pos((self.r, self.r), self.r, self.v%360),
                                                              rotate_pos((self.r, self.r), self.r, self.v%360+120),
                                                              rotate_pos((self.r, self.r), self.r, self.v%360+240)], 5)
        # 反時計回りに回る黄色の正三角形
        pg.draw.lines(self.weakpoint, (255, 255, 0), True, [rotate_pos((self.r, self.r), self.r, 360-self.v%360),
                                                            rotate_pos((self.r, self.r), self.r, 360-self.v%360+120),
                                                            rotate_pos((self.r, self.r), self.r, 360-self.v%360+240)], 5)
        pg.draw.circle(self.weakpoint, (157, 204, 224-self.v%224), (self.r, self.r), 2)  # 中心の小さい円
        self.weakpoint.set_colorkey((0, 0, 0))  # 黒を透明化
        screen.blit(self.weakpoint, self.weakpoint_rct)  # 画面に描画
        self.v += 3  # 回転角度を更新

        if self.hp < 0:  # 敵のHPが無くなったら
            self.kill()
    
    def hpbar_update(self, screen):
        """
        ターンの最後にそのターンで減ったHP分の赤いバーを減らす
        """
        pg.draw.rect(self.hpbar, self.color_dic["gray"], (0, 0, 400, 20))  # HPバーの灰色部分を描く
        for color in self.colors[:self.colors.index(self.color)]:
            pg.draw.rect(self.hpbar, self.color_dic[color], (2, 2, 396, 16))
        pg.draw.rect(self.hpbar, (255, 0, 0), (2, 2, 396*(self.turn_maxhp/self.maxhp), 16))  # HPバーの残量を描く
        pg.draw.rect(self.hpbar, self.color_dic[self.color], (2, 2, 396*(self.hp/self.maxhp), 16))  # HPバーの残量を描く
        screen.blit(self.hpbar, [10, 10])  # 画面に描画
    
    def attack(self, screen: pg.Surface, game: GameManager) -> None:
        """
        攻撃間隔が0になったら敵の攻撃を行う
        引数1 screen：画面Surface
        引数2 game：gameインスタンス
        戻り値：なし
        """
        if self.interval < 0:  # 攻撃ターンになったら
            self.img = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを用意
            self.img.fill((255, 255, 255))  # 白く塗りつぶす
            self.img.set_alpha(128)  # 半透明
            self.rct = self.img.get_rect()
            screen.blit(self.img, self.rct)  # 画面に描画
            pg.display.update()
            time.sleep(0.1)
            game.hp -= 10000  # キャラクターのHPを減らす
            self.interval = 3  # 攻撃間隔を初期化


class EnergyCircleFive(pg.sprite.Sprite):
    """
    全属性エナジーサークルクラス
    """
    def __init__(self, r: int, pos: tuple[int, int],color: tuple[int, int,int]) -> None:
        """
        イニシャライザー
        引数1 r:回転角度
        引数2 pos:キャラクターの座標タプル
        引数3 color: 色タプル
        戻り値:なし
        """
        super().__init__()
        l = 120
        self.image = pg.Surface((l, l))  # Surface作成
        pg.draw.circle(self.image, color, (l/2, l/2), l/2)
        pg.draw.circle(self.image, (0, 0, 0), (l/2, l/2), l/2-20)
        self.image.set_alpha(200)  # 透明度を設定
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = rotate_pos(pos, l-40, r)  # 発動位置をキャラクターの座標に設定
        self.attack = 5000  # 友情コンボの火力
        self.life = 100  # 発動時間

    def update(self):
        """
        発動時間を更新し、発動時間が0になったらkillする
        """
        self.life -= 1
        if self.life <= 0:
            self.kill()


class HighEnergyCircle(pg.sprite.Sprite):
    """
    エナジーサークルを管理するクラス
    """
    def __init__(self, pos):
        """
        初期化メソッド
        引数 pos:サークルの中心
        """
        super().__init__()
        self.image = pg.Surface((WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0, 0, 0))  # 黒色を透明化
        self.image.set_alpha(200)  # 透明度設定
        self.rect.center = WIDTH/2, HEIGHT/2
        self.center = pos
        self.attack = 500000  # 友情コンボのダメージ量
        self.r = 30  # 発動直後の半径
        self.t = 10  # 発動直後のエナジーサークルの幅
        self.time = 0  # 発動してからの経過時間

    def update(self):
        self.time += 1
        if self.time >= 50:
            self.r += 30
            self.t += 3
        if self.r >= WIDTH+ HEIGHT:
            self.kill()
        pg.draw.circle(self.image, (255, 0, 255), self.center, self.r+self.t)
        pg.draw.circle(self.image, (0, 0, 0), self.center, self.r)


class CrossLaser(pg.sprite.Sprite):
    """
    友情コンボ　十字レーザーを描画する
    """
    def __init__(self, r: int, pos: tuple[int, int]) -> None:
        """
        イニシャライザー
        引数1 r：回転角度
        引数2 pos：キャラクターの座標タプル
        戻り値：なし
        """
        super().__init__()
        self.image = pg.Surface((HEIGHT*2, 60))  # Surfaceの作成
        self.image.fill((0, 255, 255))  # レーザーの色を青にする
        pg.draw.rect(self.image, (255, 255, 255), (0, 13, HEIGHT*2, 34))
        self.image = pg.transform.rotate(self.image, r)  # 回転角の分だけSurfaceごと回転する
        self.image.set_alpha(200)  # 透明度を設定
        self.rect = self.image.get_rect()
        self.rect.center = pos  # 発動位置をキャラクターの座標に設定
        self.attack = 5000  # 友情コンボのダメージ量
        self.life = 100  # 発動時間

    def update(self):
        """
        発動時間を更新し、発動時間が0になったらkillする
        """
        self.life -= 1
        if self.life <= 0:
            self.kill()


class ReflectiveDiffuserBullet(pg.sprite.Sprite):
    """
    友情コンボ　反射拡散弾を描画する
    """
    def __init__(self, pos: tuple[int, int]) -> None:
        """
        イニシャライザー
        引数 pos:キャラクターの座標タプル
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
        self.rect.center = pos[0]+40, pos[1]
        self.attack = 2000  # 友情コンボのダメージ量
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


class Menu:
    """
    メニュー画面やキャラ詳細を表示
    """
    def __init__(self, bird: Bird) -> None:
        """
        イニシャライザー
        引数 bird：birdインスタンス
        """
        self.image = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを作成
        self.image.fill((0, 0, 0))   # 黒色で塗りつぶす
        self.image.set_alpha(0)  # 透明度を設定
        self.font1 = pg.font.SysFont("hgpｺﾞｼｯｸe", 30)
        self.font2 = pg.font.SysFont("hgpｺﾞｼｯｸe", 20)
        self.txt1 = self.font1.render("【" + bird.name + "】", True, (255, 255, 255))
        self.txt2 = self.font2.render("攻撃力:" + str(bird.attack), True, (255, 255, 255))
        self.txt3 = self.font2.render("スピード:" + str(bird.speed), True, (255, 255, 255))
        self.txt4 = self.font2.render("HP:" + str(bird.hp), True, (255, 255, 255))
        self.txt5 = self.font2.render("[友情コンボ]:" + bird.bump_combo_name, True, (255, 255, 255))
        self.txt6 = self.font2.render("1フレーム当たりのダメージ:" + str(bird.bump_combo_attack), True, (255, 255, 255))
        self.txt7 = self.font2.render("絵の作者:" + bird.picture_by, True, (255, 255, 255))

        self.image.blit(self.txt1, [50, 50])
        self.image.blit(self.txt2, [90, 100])
        self.image.blit(self.txt3, [90, 130])
        self.image.blit(self.txt4, [90, 160])
        self.image.blit(self.txt5, [60, 200])
        self.image.blit(self.txt6, [90, 230])
        self.image.blit(self.txt7, [350, 480])
    
    def update(self, screen: pg.Surface):
        """
        使わないときは透明化させる
        引数 screen：画面Surface
        """
        self.image.set_alpha(0)
        screen.blit(self.image, [0, 0])

    def draw(self, screen):
        """
        透明を半透明にして可視化させる
        """
        self.image.set_alpha(200)
        screen.blit(self.image, [0, 0])


class Reset:
    """
    リセットメニューを作成
    """
    def __init__(self) -> None:
        """
        イニシャライザー
        引数 ：無し
        戻り値：無し
        """
        self.image = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを作成
        self.image.fill((0, 0, 0))   # 黒色で塗りつぶす
        self.image.set_alpha(200)  # 透明度を設定
        self.font1 = pg.font.SysFont("hgpｺﾞｼｯｸe", 30)
        self.txt1 = self.font1.render("Rキーを押してリセット", True, (255, 255, 255))
        self.txt2 = self.font1.render("Mキーを押して戻る", True, (255, 255, 255))
        self.image.blit(self.txt1, [80, HEIGHT/2-50])
        self.image.blit(self.txt2, [100, HEIGHT/2+50])
        
    def draw(self, screen: pg.Surface) -> None:
        """
        リセットメニュー画面を描画
        引数 screen：画面Surface
        """
        screen.blit(self.image, [0, 0])
        pg.display.update()
        

def main():
    pg.display.set_caption("こうかとんストライク")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    game = GameManager()  # ゲームを初期化する
    birds = game.create()  # こうかとんグループを生成

    menus = []  # キャラごとの詳細画面を入れるリストを作成
    for bird in birds:
        menus.append(Menu(bird))  # 順番にMenuインスタンスを作成
    
    # BGM関係
    pg.mixer.init(frequency= 44100)  # mixerを初期化
    pg.mixer.music.set_volume(1.0)  # 音量設定
    pg.mixer.music.load("fig/bgm_1.wav")  # 爆絶BGM前半を読み込む
    pg.mixer.music.play(1)  # 1回だけ再生
    f = True  # 最後のボス戦に入った時に1回だけモンストテーマ前半を再生するための変数

    high_energy_circles = pg.sprite.Group()  # ハイエナジーサークルのグループ
    energy_circle_fives = pg.sprite.Group()  # 全属性エナジーサークルのグループ
    colors = [(255, 255, 0),  # 黄色
              (255, 0, 255),  # 紫色
              (255, 0, 0),    # 赤色
              (0, 255, 255),  # 青色
              (127, 255, 0)]  # 緑色
    cross_lasers = pg.sprite.Group()  # 十字レーザーのグループ
    reflective_diffuser_bullets = pg.sprite.Group()  # 反射各散弾のグループ

    # 味方関係
    turn_character = pg.Surface((80, 80))
    turn_character_rct = turn_character.get_rect()
    bump_f = True  # 友情コンボが画面上に存在しない事を確認する変数
    
    # 敵関係
    enemy_list = ["唐揚げ", "手羽先", "ローストチキン"]  # 敵のリスト
    enemys = pg.sprite.Group()  # 敵グループを作成
    enemy = Enemy(enemy_list[0])  # 最初の敵を生成
    enemys.add(enemy)  # 最初の敵をグループに入れる

    # ゲームクリア画面関係
    clear_img = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを用意
    clear_img.fill((0, 0, 0))  # 黒く塗りつぶす
    clear_img.set_alpha(128)  # 半透明
    font = pg.font.Font(None, 80)  #文字サイズを80に設定
    txt = font.render("Game Clear !", True, (255, 255, 255))  # 文字を作成
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH/2, HEIGHT/2  # 文字の中心を画面中央に設定
    clear_img.blit(txt, txt_rct)  # ゲームクリア画面に描画

    # ゲームクリア画面関係
    go_img = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを用意
    go_img.fill((0, 0, 0))  # 黒く塗りつぶす
    go_img.set_alpha(128)  # 半透明
    font2 = pg.font.Font(None, 80)  #文字サイズを80に設定
    txt = font2.render("Game Over !", True, (255, 255, 255))  # 文字を作成
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH/2, HEIGHT/2  # 文字の中心を画面中央に設定
    go_img.blit(txt, txt_rct)  # ゲームクリア画面に描画

    # メニュー画面関係
    menu_f = False  # メニュー画面が開かれているかを保存する変数
    reset = Reset()

    tmr = 0
    clock = pg.time.Clock()
    while True:
        # BGM関係
        if not pg.mixer.music.get_busy():  # 音楽が止まった時
            if game.state == "initial":  # 始まってすぐ
                pg.mixer.music.load("fig/bgm_2.wav")  # 爆絶BGM後半を読み込む
                pg.mixer.music.play(-1)  # 音楽をループで再生
                game.state = "wait"  # ゲームを開始
            if enemy_list[0] == "ローストチキン" and (not f):  # ラスボスが出てきた時
                pg.mixer.music.load("fig/theme_2.wav")  # モンストテーマ後半を読み込む
                pg.mixer.music.play(-1)  # 音楽をループで再生

        key_lst = pg.key.get_pressed()  # 押されたkey
        mouse_pos = pg.mouse.get_pos()  # マウスの座標
        # event処理
        for event in pg.event.get():
            # ×ボタンをクリックした時
            if event.type == pg.QUIT:
                return
            # keyを押した時(1回のみ)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_m:
                    menu_f = False if menu_f else True
                if event.key == pg.K_r and menu_f:
                    game = GameManager()  # ゲームを初期化する
                    birds = game.create()  # こうかとんグループを生成

                    menus = []  # キャラごとの詳細画面を入れるリストを作成
                    for bird in birds:
                        menus.append(Menu(bird))  # 順番にMenuインスタンスを作成
                    
                    # BGM関係
                    pg.mixer.init(frequency= 44100)  # mixerを初期化
                    pg.mixer.music.set_volume(1.0)  # 音量設定
                    pg.mixer.music.load("fig/bgm_1.wav")  # 爆絶BGM前半を読み込む
                    pg.mixer.music.play(1)  # 1回だけ再生
                    f = True  # 最後のボス戦に入った時に1回だけモンストテーマ前半を再生するための変数

                    high_energy_circles = pg.sprite.Group()  # ハイエナジーサークルのグループ
                    energy_circle_fives = pg.sprite.Group()  # 全属性エナジーサークルのグループ
                    colors = [(255, 255, 0),  # 黄色
                            (255, 0, 255),  # 紫色
                            (255, 0, 0),    # 赤色
                            (0, 255, 255),  # 青色
                            (127, 255, 0)]  # 緑色
                    cross_lasers = pg.sprite.Group()  # 十字レーザーのグループ
                    reflective_diffuser_bullets = pg.sprite.Group()  # 反射各散弾のグループ

                    # 味方関係
                    turn_character = pg.Surface((80, 80))
                    turn_character_rct = turn_character.get_rect()
                    bump_f = True
                    
                    # 敵関係
                    enemy_list = ["唐揚げ", "手羽先", "ローストチキン"]  # 敵のリスト
                    enemys = pg.sprite.Group()  # 敵グループを作成
                    enemy = Enemy(enemy_list[0])  # 最初の敵を生成
                    enemys.add(enemy)  # 最初の敵をグループに入れる

                    # ゲームクリア画面関係
                    clear_img = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを用意
                    clear_img.fill((0, 0, 0))  # 黒く塗りつぶす
                    clear_img.set_alpha(128)  # 半透明
                    font = pg.font.Font(None, 80)  #文字サイズを80に設定
                    txt = font.render("Game Clear !", True, (255, 255, 255))  # 文字を作成
                    txt_rct = txt.get_rect()
                    txt_rct.center = WIDTH/2, HEIGHT/2  # 文字の中心を画面中央に設定
                    clear_img.blit(txt, txt_rct)  # ゲームクリア画面に描画

                    # ゲームクリア画面関係
                    go_img = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを用意
                    go_img.fill((0, 0, 0))  # 黒く塗りつぶす
                    go_img.set_alpha(128)  # 半透明
                    font2 = pg.font.Font(None, 80)  #文字サイズを80に設定
                    txt = font2.render("Game Over !", True, (255, 255, 255))  # 文字を作成
                    txt_rct = txt.get_rect()
                    txt_rct.center = WIDTH/2, HEIGHT/2  # 文字の中心を画面中央に設定
                    go_img.blit(txt, txt_rct)  # ゲームクリア画面に描画

                    # メニュー画面関係
                    menu_f = False  # メニュー画面が開かれているかを保存する変数
                    reset = Reset()
                    tmr = 0
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
        if menu_f:
            reset.draw(screen)
            continue

        # 敵関係
        if game.state == "wait":
            turn_character_rct.center = game.now_character().rect.center
            pg.draw.circle(turn_character, (255, 255, 0), (40, 40), 40)
            pg.draw.circle(turn_character, (0, 0, 0), (40, 40), 35)
            turn_character.set_colorkey((0, 0, 0))
            screen.blit(turn_character, turn_character_rct)
        enemys.draw(screen)  # 敵を描画
        enemys.update(screen)  # 敵の状態を更新(弱点描画)

        # 友情コンボ関係
        if game.state == "move":  # 手版のキャラクターが動いているとき（敵にダメージを与えられるとき）
            # 手版のキャラクターと0のキャラクターとの衝突判定
            if game.now_character().rect.colliderect(game.now_character(0).rect) and game.now_character(0).bump_combo:
                if game.turn%4 != 0:
                    for r, color in zip(range(-90, 261, 72), colors):
                        energy_circle_fives.add(EnergyCircleFive(r, game.now_character(0).rect.center, color))
                        game.now_character(0).bump_combo = False
            # 手番のキャラクターと1のキャラクターとの衝突判定
            if game.now_character().rect.colliderect(game.now_character(1).rect) and game.now_character(1).bump_combo:
                if game.turn%4 != 1:
                    for r in range(0, 91, 90):
                        cross_lasers.add(CrossLaser(r, game.now_character(1).rect.center))
                        game.now_character(1).bump_combo = False
            # 手番のキャラクターと2のキャラクターとの衝突判定
            if game.now_character().rect.colliderect(game.now_character(2).rect) and game.now_character(2).bump_combo:
                if game.turn%4 != 2:
                    for i in range(10):
                        reflective_diffuser_bullets.add(ReflectiveDiffuserBullet(game.now_character(2).rect.center))
                    game.now_character(2).bump_combo = False
            #  手番のキャラクターと3のキャラクターとの衝突判定
            if game.now_character().rect.colliderect(game.now_character(3).rect) and game.now_character(3).bump_combo:
                if game.turn%4 != 3:
                    high_energy_circles.add(HighEnergyCircle(game.now_character(3).rect.center))
                    game.now_character(3).bump_combo = False
        energy_circle_fives.update()
        energy_circle_fives.draw(screen)
        cross_lasers.update()
        cross_lasers.draw(screen)
        reflective_diffuser_bullets.update()
        reflective_diffuser_bullets.draw(screen)
        high_energy_circles.update()
        high_energy_circles.draw(screen)

        game.update(screen, tmr, bump_f)  # ゲーム進行を更新する
        if game.state == "drag":  # 矢印を引っ張ている間
            arrow.draw_(mouse_pos, game.now_character().rect.center, screen)  # 矢印を描画
        
        if game.state == "move":  # 手番のキャラクターが動いているとき(敵にダメージを与えられるとき)
            # キャラクターと敵の衝突判定
            if pg.sprite.spritecollide(game.now_character(), enemys, False):  # 敵を殴ったら
                for enemy in enemys:
                    enemy.hp -= game.now_character().attack  # 敵に手番のキャラクターの攻撃力のダメージを与える
            # 手番のキャラクターと弱点の衝突判定
            if game.now_character().rect.colliderect(enemy.weakpoint_rct):  # 弱点を殴ったら
                for enemy in enemys:
                    enemy.hp -= game.now_character().attack*2  # 敵に手番のキャラクターの攻撃力2倍のダメージを与える
            
            # 友情コンボ：十字レーザーと敵の衝突判定
            # 敵と友情コンボの当たり判定
            for obj in pg.sprite.groupcollide(cross_lasers, enemys, False, False).keys():
                for enemy in enemys:
                    enemy.hp -= obj.attack  # 敵に友情コンボのダメージを与える
            # 弱点と友情コンボの当たり判定
            for obj in cross_lasers:
                for enemy in enemys:
                    if enemy.weakpoint_rct.colliderect(obj.rect):
                        enemy.hp -= obj.attack*2  # 敵に友情コンボの2倍ダメージを与える
            
            # 友情コンボ：全属性エナジーサークルと敵の衝突判定
            # 敵と友情コンボの当たり判定
            for obj in pg.sprite.groupcollide(energy_circle_fives, enemys, False, False).keys():
                for enemy in enemys:
                    enemy.hp -= obj.attack  # 敵に友情コンボのダメージを与える
            # 弱点と友情コンボの当たり判定
            for obj in energy_circle_fives:
                for enemy in enemys:
                    if enemy.weakpoint_rct.colliderect(obj.rect):
                        enemy.hp -= obj.attack*2  # 敵に友情コンボの2倍ダメージを与える
            
            # 友情コンボ：ハイエナジーサークルと敵の衝突判定
            # 敵と友情コンボの当たり判定
            for obj in high_energy_circles:
                for enemy in enemys:
                    d = math.dist(game.now_character(3).rect.center, enemy.rect.center)
                    if d <= obj.r:
                        enemy.hp -= obj.attack  # 敵に友情コンボのダメージを与える
                    # 弱点と友情コンボの当たり判定
                    d2 = math.dist(game.now_character(3).rect.center, enemy.weakpoint_rct.center)
                    if d2 <= obj.r:
                        enemy.hp -= obj.attack*2  # 敵に友情コンボの2倍ダメージを与える
                        obj.attack = 0
            
            # 友情コンボ：反射拡散弾と敵の衝突判定
            # 敵と友情コンボの当たり判定
            for obj in pg.sprite.groupcollide(reflective_diffuser_bullets, enemys, False, False).keys():
                for enemy in enemys:
                    enemy.hp -= obj.attack  # 敵に友情コンボのダメージを与える
            # 弱点と友情コンボの当たり判定
            for obj in reflective_diffuser_bullets:
                for enemy in enemys:
                    if enemy.weakpoint_rct.colliderect(obj.rect):
                        enemy.hp -= obj.attack*2  # 敵に友情コンボの2倍ダメージを与える

        for mouse_pressed in pg.mouse.get_pressed():  # マウスの押下情報を取得
            if mouse_pressed:
                # マウスを押している間
                m_pos = pg.mouse.get_pos()  # 現在のマウスカーソル座標を取得
                for i, menu in enumerate(menus):  # キャラ詳細画面のインスタンスを順に回す
                    if 10+100*i < m_pos[0] < 10+100*i+90 and 575 < m_pos[1] < 665:  # キャラを押したら
                        menu.draw(screen)  # キャラ詳細画面を描画
                    else:
                        menu.update(screen)  # キャラ詳細画面を透明化

        # 更新処理
        if len(high_energy_circles) == 0 and len(energy_circle_fives) == 0 and len(cross_lasers) == 0 and len(reflective_diffuser_bullets) == 0:
            # 友情コンボが画面上に存在しない時
            bump_f = True
        else:  # 友情コンボが画面上に存在する時
            bump_f = False
        if len(enemys) == 0 and game.now_character().speed > 0 and tmr%5 == 0 and len(enemy_list) == 1:  # 最後の敵を倒したら
            game.now_character().speed -= 1
        if game.state == "end_process":  # ターンが終了したら
            if len(enemys) == 0:  # 敵のHPが0になったら
                del enemy_list[0]  # 倒した敵をリストから消す
                try:
                    enemy = Enemy(enemy_list[0])  # 新たな敵を生成
                    game.hp = game.maxhp 
                    for chara in birds:
                        l = math.dist(enemy.rect.center, chara.rect.center)
                        if l < 90+30:
                            x = (chara.rect.centerx - enemy.rect.centery)/l*(90+30-l)
                            y = (chara.rect.centery - enemy.rect.centery)/l*(90+30-l)
                            chara.rect.move_ip(x, y)
                except IndexError:  # ゲームクリア
                    screen.blit(clear_img, [0, 0])  # クリア画面を描画
                    pg.mixer.music.fadeout(1000)
                    pg.display.update()
                    time.sleep(5)
                    return
                enemys.add(enemy)  # 新たな敵をグループに入れる
                # BGM関係
                if enemy_list[0] == "ローストチキン" and f:  # ラスボスが出てきたら＆最初の1回のみ
                    pg.mixer.music.set_volume(0.2)  # 音量を調整
                    pg.mixer.music.load("fig/theme_1.wav")  # モンストテーマ前半を読み込む
                    pg.mixer.music.play(1)  # 1回だけ再生
                    f = False  # フラグをFalseにする
            else:
                for enemy in enemys:
                    enemy.interval -= 1  # 攻撃間隔を1減らす
                    enemy.attack(screen, game)  # 攻撃(一定ターンのみ)
                    while enemy.turn_maxhp >= enemy.hp:  # 赤いバーが残りHPバーと同じになるまで
                        # print(enemy.turn_maxhp, enemy.hp)
                        enemy.turn_maxhp -= enemy.maxhp/100  # 赤いバーを少しずつ減らす
                        enemy.hpbar_update(screen)  # HPバーを更新
                        enemys.draw(screen)
                        pg.display.update()
                        clock.tick(60)
                    else:
                        enemy.turn_maxhp = enemy.hp
            game.update(screen, tmr, bump_f)
            game.end_process()  # ターンの最終処理をする
            if game.hp <= 0:
                screen.blit(go_img, [0, 0])  # ゲームオーバー画面を描画
                pg.display.update()
                time.sleep(5)
                return
        pg.display.update()
        tmr += 1
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()