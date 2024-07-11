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
        self.bump_combo = True  # 友情コンボがこのターンで発動されたかを保存する
    
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
        self.hp = 1000000  # HPを設定
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
            game.hp -= 400  # キャラクターのHPを減らす
            self.interval = 3  # 攻撃間隔を初期化


def main():
    pg.display.set_caption("こうかとんストライク")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")
    game = GameManager()  # ゲームを初期化する
    birds = game.create()  # こうかとんグループを生成

    # 味方関係
    turn_character = pg.Surface((80, 80))
    turn_character_rct = turn_character.get_rect()
    
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

    tmr = 0
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

        if game.state == "wait":
            turn_character_rct.center = game.now_character().rect.center
            pg.draw.circle(turn_character, (255, 255, 0), (40, 40), 40)
            pg.draw.circle(turn_character, (0, 0, 0), (40, 40), 35)
            turn_character.set_colorkey((0, 0, 0))
            screen.blit(turn_character, turn_character_rct)

        enemys.draw(screen)  # 敵を描画
        enemys.update(screen)  # 敵の状態を更新(弱点描画)

        game.update(screen, tmr)  # ゲーム進行を更新する
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
            
            # # 敵と友情コンボの当たり判定　obj_g:友情コンボのグループ
            # for obj in pg.sprite.groupcollide(obj_g, enemys, False, False).keys():
            #     for enemy in enemys:
            #         enemy.hp -= obj.attack  # 敵に友情コンボのダメージを与える

            # # 弱点と友情コンボの当たり判定
            # for obj in obj_g:
            #     for enemy in enemys:
            #         if enemy.week.colliderect(obj.rect):
            #             enemy.hp -= obj.attack*2  # 敵に友情コンボの2倍ダメージを与える

        # 更新処理
        if game.state == "end_process":  # ターンが終了したら
            if len(enemys) == 0:  # 敵のHPが0になったら
                del enemy_list[0]  # 倒した敵をリストから消す
                try:
                    enemy = Enemy(enemy_list[0])  # 新たな敵を生成
                except IndexError:  # ゲームクリア
                    screen.blit(clear_img, [0, 0])  # クリア画面を描画
                    pg.display.update()
                    time.sleep(5)
                    return
                enemys.add(enemy)  # 新たな敵をグループに入れる
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
            game.end_process()  # ターンの最終処理をする
        pg.display.update()
        tmr += 1
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()