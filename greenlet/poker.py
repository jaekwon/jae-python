import random
#from py.magic import greenlet
from greenlet import greenlet
import pdb

# set up logging
import logging
logging.basicConfig(format="%(name)-20s:\t%(message)s")
logging.debug("program started.")

def random_move(legal_moves):
	return random.choice(legal_moves)

FOLD = "fold"
CALL = "call"
BET = "bet"

class Player(greenlet):

	def __init__(self, name):
		self.name = name
		super(Player, self).__init__(self.run, name)
		self.bank = 1000
		self.log = logging.getLogger(name)

	def bring_to_game(self, game):
		self.game = game
	
	def run(self):
		while True:
			move = random_move(self.legal_moves)
			self.log.info("[%s] - %s" % (move, str(self.dealt_card)))
			self.game.switch(move)
		#while True

class Player1(Player):
	def __init__(self, name):
		super(type(self), self).__init__(name);
		self.last_game = None

	def run(self):
		while True:
			move = random_move(self.legal_moves)
			self.log.info("gameid: %d" % self.game.game_index)	
			self.game.switch(move)
		

class IllegalMoveException(Exception):
	pass

class NewRound(Exception):
	pass

class NewStage(Exception):
	pass

class SimpleGame(greenlet):
	
	def __init__(self):
		super(SimpleGame, self).__init__(self.run, "^^game^^")
		self.log = logging.getLogger("simple game")

		self.level = 1
		self.players = [Player1("^^%s^^" % x) for x in range(2)]
		for player in self.players:
			player.bring_to_game(self)
		self.set_debug()


	def set_debug(self):
		for player in self.players:
			player.log.setLevel(logging.INFO)
		self.log.setLevel(logging.WARN)
		
	def deal(self, target_player = None):
		if target_player == None:
			for player in self.players:
				player.dealt_card = []
				for i in range(2):
					dealt = random.choice(list(self.cards))
					self.cards.remove(dealt)
					player.dealt_card.append(dealt)
		else:
			target_player.dealt_card = dealt = random.choice(list(self.cards))
			self.cards.remove(dealt)

	def run(self):
		print "starting new round"

		self.playeri = PlayerIterator(self.players, 0)
		self.playeri.mark()
		self.game_index = 0;

		for _ in range(100):
			try:
				self.moves = []

				self.table_money = 0
				self.playeri.reset()
				self.playeri.next()	# move button over
				self.playeri.mark() # put button down? 
				self.cards = set(range(52))
				self.game_index = self.game_index + 1

				def collect_money(player, blinds):
					money = blinds * self.level
					self.table_money += money
					player.bank -= money
					self.log.info("%s put $%d" % (player.name, money))

				def reward_pot(player):
					player.bank += self.table_money
					self.log.warn("%s wins pot $%d" % (player.name, self.table_money))
					self.table_money = 0

				def legal_moves():
					moves = [FOLD, CALL, BET]
					if self.bet_level == 0:
						moves.remove(FOLD)
					if self.bet_level == 4:
						moves.remove(BET)
					return moves

				for i in ['single']:	# simple game

					self.stage = i
					self.playeri.reset()
					self.bet_level = 0
					self.player_bet_levels = {}
					self.last_bettor = None
					self.log.warn(" ------   %s of game   ------ " % i)

					# deal cards	
					for player in self.players:
						self.player_bet_levels[player] = 0
						if self.stage != 'preflop':
							self.deal(player)
					if self.stage == 'preflop':
						self.deal()

					try:
						for player in self.playeri:
							self.log.debug("switching to player %s" % str(player.name))
							player.legal_moves = legal_moves()
							player_move = player.switch()
							self.moves.append((player, player_move))
					
							if player_move == FOLD:
								self.playeri.remove()
								self.log.info("player %s folded" % str(player.name))

								# reward pot to last player
								if len(self.playeri) == 1:
									reward_pot(self.playeri.current())
									raise NewRound, "player %s won" % self.playeri.current().name

							elif player_move == CALL:
								self.log.info("player %s called" % str(player.name))
								called_blinds = self.bet_level - self.player_bet_levels[player]
								collect_money(player, called_blinds)
								self.player_bet_levels[player] = self.bet_level
								if [self.player_bet_levels[x] for x in self.playeri.players] == [self.bet_level]*len(self.playeri):
									raise NewStage, "all players called, new stage coming"
							elif player_move == BET:
								self.log.info("player %s bet" % str(player.name))
								self.last_bettor = player
								self.bet_level += 1
								bet_blinds = self.bet_level - self.player_bet_levels[player]
								collect_money(player, bet_blinds)
								self.player_bet_levels[player] = self.bet_level
							else:
								raise IllegalMoveException, "unknown move!"
					except NewStage, e:
						self.log.debug(e.message)
				#for i in ['preflop', 'flop', 'turn', 'river']: # three stages

				#check cards and reward pot to someone
				remaining_players = self.playeri.players
				if self.last_bettor:	
					remaining_players.append(self.last_bettor)
				winner = max(remaining_players, key=lambda x: x.dealt_card)
				reward_pot(winner)

				raise NewRound, "showdown"
			except NewRound:	
				self.log.warn(" ---------- new round! ---------- ");	
		#while True
		
		for player in self.players:
			print "player %s:\t%d" % (player.name, player.bank)
						
					
class PlayerIterator(object):
	"""
		a = poker.PlayerIterator(['a', 'b', 'c', 'e'], 0)
		a.current() # 'a'
		a.get(0)	# 'a'
		a.get(-1)	# 'e'
		a.next()	# 'a'
		a.next()	# 'b'
		a.get(-1)	# 'a'
	
		for i in a:
			print i	# loops forever

	"""
	
	def __init__(self, players, offset):
		assert 0 <= offset < len(players)
		self._all_players = players[:]
		self.players = players[:]
		self.offset = (offset - 1) % len(players)
	
	def __iter__(self):
		return self

	def next(self):	
		self.offset = (self.offset + 1) % len(self.players)
		return self.players[self.offset]

	def current(self):
		return self.players[self.offset]

	def get(self, relative_index):
		return self.players[(self.offset + relative_index) % len(self.players)]

	def mark(self):
		self._mark = self.offset

	def reset(self):
		self.players = self._all_players[:]
		self.offset = self._mark

	def remove(self):
		"""	Remove current user temporarily from this iterator. 
			calling "current" will return the previous user
		"""
		if self.players:
			del self.players[self.offset]
			if self.players:
				self.offset = (self.offset - 1) % len(self.players)
		else:
			raise EmptyException, "cannot remove from an empty list of players"

	def __len__(self):
		return len(self.players)

game = SimpleGame()
game.switch()		
