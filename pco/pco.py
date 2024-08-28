
import tkinter as tk
from tkinter import *
import json
class Alien(object):
    def __init__(self):
        self.id = None
        self.alive = True
        self.x_speed=25
        self.width,self.height=70,50
        self.img=tk.PhotoImage(file='alien.gif')

    def touched_by(self, canvas,projectile):

            projectile.shooter.fired_bullets.remove(projectile)
            canvas.delete(projectile.id)
            self.alive=False
   
    def install_in(self, canvas, x, y):

        self.canvas=canvas
        self.id=canvas.create_image(x,y,image=self.img,tags="alien") 
    #x1 et x2 corespondent aux abcisses des aliens aux extrémités
    def move_in(self,x1,x2):

        canvas_width = int(self.canvas.cget("width"))
        self.y_speed=0

        if x2>canvas_width:

            self.x_speed= -self.x_speed
            self.y_speed=10

        elif x1< 0:

            self.x_speed = -self.x_speed
            self.y_speed=10

        self.canvas.move(self.id, self.x_speed,self.y_speed)


class Fleet(object):
    def __init__(self):
        self.aliens_lines = 5
        self.aliens_columns = 10
        self.aliens_inner_gap =20
        self.explosion=tk.PhotoImage(file='explosion.gif')
        self.fleet_size =self.aliens_lines * self.aliens_columns
        self.aliens_fleet= [None] * self.fleet_size
        self.is_AtBottom=False
        for i in range(0,self.fleet_size):
            self.aliens_fleet[i]=Alien()

    def get_fleet_width(self):
        alien_width = self.aliens_fleet[0].width
        return alien_width*(self.aliens_columns+6)+(self.aliens_inner_gap*(self.aliens_columns-1))

    def install_in(self, canvas):
        alien_width , alien_height =self.aliens_fleet[0].width,self.aliens_fleet[0].height
        self.canvas=canvas

        for i in range(0,self.fleet_size):
            #(50,50) sont les coordonnées initiales de la fleet, i%10 et i//10 respectivement la colonne et la ligne de l'alien à installer
            #La position de chaque alien est (sa largeur+l'espacement entre deux aliens)*sa colonne
            self.aliens_fleet[i].install_in(canvas,110+(alien_width+self.aliens_inner_gap)*(i%10),110+(alien_height+self.aliens_inner_gap)*(i//10))

    def move_in(self):
        canvas_height= int(self.canvas.cget("height"))
        x1,_, x2,y2 = self.canvas.bbox("alien")
        #Tant que la fleet n'a pas atteint le bas, on déplace les aliens
        if y2<canvas_height-50:

            for alien in self.aliens_fleet:
                alien.move_in(x1,x2)

        else:
            self.is_AtBottom=True

    def manage_touched_aliens_by(self,canvas,defender,score):
        #pour chaque alien de la fleet, on verifie si une des balles tirées l'a touché;
        #on recherche ensuite la balle qui l'a toucheé;L'alien et la balle sont alors supprimé et une explosion apparait.
        #on s'arrete quand on a plus aucun alien dans la fleet
        for alien in self.aliens_fleet:
            x1, y1, x2, y2 = canvas.bbox(alien.id)
            overlapped = canvas.find_overlapping(x1, y1, x2, y2)
            #Si l'alien croise une balle alors il n'est plus en vie et la balle est supprimée.
            if len(overlapped)==3:
                for bullet in defender.fired_bullets:
                    #overlapped[0] est l'alien et overlapped[1] est la balle qui l'a touché
                    if(bullet.id==overlapped[2]):
                        alien.touched_by(canvas,bullet)
                        score+=100
                        break

            if alien.alive==False:
                x, y,_,_ = self.canvas.bbox(alien.id)
                explosion_image=canvas.create_image(x,y,image=self.explosion,tags="explosion")
                canvas.after(70,canvas.delete,explosion_image)
                self.aliens_fleet.remove(alien)
                canvas.delete(alien.id)

            if len(self.aliens_fleet)==0:
                break
        return score
class Defender(object):
    def __init__(self,canvas):
        self.id=None
        self.canvas=canvas
        self.width = 20
        self.height = 20
        self.speed= 20
        self.max_fired_bullets = 8
        self.fired_bullets = []
        self.space=tk.PhotoImage(file='spaceship.gif')

    def install_in(self):
        canvas_width=int(self.canvas.cget("width"))
        canvas_height=int(self.canvas.cget("height"))
        self.id = self.canvas.create_image(canvas_width//2-self.width//2,canvas_height-self.height,image=self.space)
    
    def fire(self, canvas):
        if(len(self.fired_bullets)<self.max_fired_bullets):
            bullet=Bullet(self)
            self.fired_bullets.append(bullet)
            bullet.install_in(canvas)
        
class Bullet(object):
    def __init__(self, shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 25
        self.id = None
        self.shooter = shooter
        self.nb_mouvement=0

    def install_in(self, canvas):
        x,y,x2,_=canvas.bbox(self.shooter.id) #coordonées du tireur (defendeur)
        self.id=canvas.create_oval((x2+x)//2-self.radius,y-self.radius,(x2+x)//2+self.radius,y+self.radius,fill=self.color)

    def move_in(self,canvas):
        canvas_height=int(canvas.cget("height"));
        self.total_mouvement=canvas_height/self.speed
        #On déplace la balle puis on incrémente son nombre de mouvements effectués,il servira à détecter lorsque la balle doit etre supprimée.
        self.nb_mouvement+=1
        canvas.move(self.id,0,-self.speed)

class Score(object):
    def __init__(self,player,score):

        self.player=player
        self.score=score
        #On essaie d'ouvrir notre fichier json; si on réussi, on récupère tous les scores,
        # si on réussit pas, alors le fichier n'existe pas on initialise alors les autres scores à vide
        try:
            scores_file=open("scores.json","r")
            self.other_scores=json.load(scores_file)
        except:
            self.other_scores=[]

        self.list=self.other_scores[:]
    #Ajout du score final dans le fichier json
    def saveScore(self):

        score_file=open("scores.json","w")
        tmp=self.other_scores
        scores={}
        scores["joueur"]=self.player
        scores["score"]=self.score
        tmp.append(scores)
        json.dump(tmp,score_file)
    
    @classmethod
    #On crée des éléments de type score dans self.list
    def fromFile(cls):

        f = open("scores.json","r")
        tmp = json.load(f)
        cls.liste = []

        for d in tmp:

            l=Score(d["joueur"],d["score"])
            cls.liste.append(l)

        return cls.liste

    def highScore(self):
        #On récupère le score à partir d'un élément de type score
        def getScore(Score):
            return Score.score
        #Dans le cas ou  le fichier n'est pas encore crée, quand on lance le jeu on affiche rien.
        try:
            l=Score.fromFile()
        except:
            l=[]
        #Fonction de tri à l'envers.
        self.list=sorted(l,key=getScore,reverse=True)
        
        return self.list
       
class Game(object):

    def __init__(self, frame):
        self.frame = frame
        self.fleet = Fleet()
        self.height =700
        self.width = self.fleet.get_fleet_width()
        self.isWon=None
        self.score_act=0
        self.player=None
        self.final_score=Score(self.player,self.score_act)
        self.high_scores =self.final_score.highScore()
        self.canvas = tk.Canvas(self.frame,width=self.width,height=self.height,bg="black")
        self.canvas.pack()
        self.score_text=None
    def background(self):
        self.bk = tk.PhotoImage(file="stars-space.gif")
        self.canvas.create_image(self.width//2,500,image=self.bk)
    def start(self):
        self.background()
        self.isWon=None
        self.fleet=Fleet()
        self.defender = Defender(self.canvas)
        self.defender.install_in()
        self.fleet.install_in(self.canvas)
        self.frame.winfo_toplevel().bind("<Key>", self.keypress)
    def get_score(self):

        texte="Score: "+str(self.score_act)
        if self.score_text!=None:
            self.canvas.delete(self.score_text)
        self.score_text=self.canvas.create_text(100, 50, text=texte, fill="#00F400", font=('Impact 25'))
    def animation(self):
        self.get_score()
        if(self.isWon==None):
            self.fleet.move_in()
        self.score_act=self.fleet.manage_touched_aliens_by(self.canvas,self.defender,self.score_act)
        self.move_bullets()
        self.checkStatus()
        if self.isWon==None:
            self.canvas.after(150,self.animation)
        else:
            self.final_score=Score(self.player,self.score_act)
            self.final_score.saveScore()
            self.high_scores =self.final_score.highScore()
            self.fin(self.isWon)
    def start_animation(self):
        self.canvas.delete("all")
        self.start()
        self.animation()
    #mouvement du defender et tire des balles
    def keypress(self,event):
        try:
            x,_,x2,_=self.canvas.bbox(self.defender.id)
            if event.keysym=="Left":
                if x>self.defender.width:
                    self.canvas.move(self.defender.id,-20,0)
            elif event.keysym=="Right":
                if x2<self.width-self.defender.width:
                    self.canvas.move(self.defender.id,20,0)
            elif event.keysym=="space":
                self.defender.fire(self.canvas)
            elif event.keysym=="Escape":
                self.isWon=False
        except:
            None
        
    #deplacement des bullets
    def move_bullets(self):
        for bullet in self.defender.fired_bullets:
            bullet.move_in(self.canvas)
            #pour chaque balle, on compare son nombre de mouvements déjà effectués au nombre total de mouvement qu'il ferait si il atteint le haut
            #si elle atteint le haut, alors elle est supprimée.
            if bullet.nb_mouvement>=bullet.total_mouvement:
                self.defender.fired_bullets.remove(bullet)
                self.canvas.delete(bullet.id)
                self.score_act-=10
                self.get_score()
    #On verifie si la partie est gagnée ou pas, elle est gagnée si il n'y a plus d'alien dans la fleet et perdue si la fleet est arrivée en bas
    def checkStatus(self):
        if len(self.fleet.aliens_fleet)==0:
            self.score_act+=100
            self.isWon=True
        elif self.fleet.is_AtBottom==True:
            self.isWon=False

    def menu(self):
        self.canvas.delete("all")
        self.background()
        def new_game():
            label=tk.Label(self.canvas, text="Entrer votre nom", font=("Impact", 17), fg='#FDFD0F', bg='black')
            self.canvas.create_window(self.max_w//2-100,330,window=label)
            self.name_entry = Entry(self.canvas,width=30)
            self.canvas.create_window(self.max_w/2-100,360,window=self.name_entry)
        def getname():
            if self.name_entry.get() !="":
                self.player=self.name_entry.get()
            else:
                self.player="Anynyme"
            self.start_animation()
        self.max_w = int(self.canvas.cget("width"))
        self.space_title=tk.PhotoImage(file="spacetitle.gif")
        self.canvas.create_image(self.max_w//2,150,image=self.space_title)
        txt_ng="New game"
        label=tk.Button(self.canvas, text=txt_ng, font=("Impact", 15), fg='#FDFD0F', bg='black',borderwidth="0",command=getname)
        self.canvas.create_window(self.max_w//2-100,400,window=label)
        txt_quit="Quit"
        label=tk.Button(self.canvas, text=txt_quit, font=("Impact", 30), fg='#FDFD0F', bg='black',borderwidth="0",command=self.frame.quit)
        self.canvas.create_window(self.max_w//2,600,window=label)
        label=tk.Label(self.canvas, text="High Scores", font=("Impact", 20), fg='#FDFD0F', bg='black')
        self.canvas.create_window(self.max_w//2+160,330,window=label)
        self.canvas.create_rectangle(self.max_w//2+60,330,self.max_w//2+265,560,width=2,outline="white")
        y=i=0
        score=self.high_scores
        def high(y,i):
            try:
                label=tk.Label(self.canvas, text=str(score[i].player)+":"+str(score[i].score), font=("Impact light", 15), fg='white', bg='black')
                self.canvas.create_window(self.max_w//2+160,370+y,window=label)
                if(i<4):
                    self.canvas.after(150,high,y+40,i+1)
            except:
                None
        
        high(y,i)
        new_game()
    def fin(self,x):
        self.canvas.delete("all")
        self.background()
        if x ==True:
            label=tk.Label(self.canvas, text="Felicitation, vous avez gagné!", font=("Impact",60), fg='#00F400', bg='black')
            self.canvas.create_window(self.max_w//2,330,window=label)
            label1=tk.Button(self.canvas, text="Quit", font=("Impact", 30), fg='green', bg='white',borderwidth="0",command=self.frame.quit)
            self.canvas.create_window(self.max_w//2-100,600,window=label1)
            labe2=tk.Button(self.canvas, text="Rejouer", font=("Impact", 30), fg='green', bg='white',borderwidth="0",command=self.menu)
            self.canvas.create_window(self.max_w//2+100,600,window=labe2)
        else: 
            label=tk.Label(self.canvas, text="Dommage, vous avez perdu!", font=("Impact", 60), fg='#00F400', bg='black')
            self.canvas.create_window(self.max_w//2,330,window=label)
            label1=tk.Button(self.canvas, text="Quit", font=("Impact", 30), fg='green', bg='white',borderwidth="0",command=self.frame.quit)
            self.canvas.create_window(self.max_w//2-100,600,window=label1)
            labe2=tk.Button(self.canvas, text="Rejouer", font=("Impact", 30), fg='green', bg='white',borderwidth="0",command=self.menu)
            self.canvas.create_window(self.max_w//2+100,600,window=labe2)
class SpaceInvaders(object):
    """
     Main Game class
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both")
        self.game = Game(self.frame)

    def play(self):
        self.game.menu()
        self.root.mainloop()
    

SpaceInvaders().play()