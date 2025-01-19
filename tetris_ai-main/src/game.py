from board import Board
from time import sleep
from greedy import Greedy_AI
from copy import deepcopy
from genetic import Genetic_AI
from mcts import MCTS_AI
from piece import Piece
import pygame


BLACK = 0, 0, 0
WHITE = 255, 255, 255
GREEN = (0, 255, 0)

class Game:
    def __init__(self, mode, agent=None):
        self.board = Board()
        self.curr_piece = Piece()
        self.y = 20
        self.x = 5
        self.screenWidth = 500
        self.screenHeight = 1000
        self.top = 0
        self.pieces_dropped = 0
        self.rows_cleared = 0
        self.score = 0  # Initialize score

        if mode == "greedy":
            self.ai = Greedy_AI()
        elif mode == "genetic":
            if agent == None:
                self.ai = Genetic_AI()
            else:
                self.ai = agent
        elif mode == "mcts":
            self.ai = MCTS_AI()
        else:
            self.ai = None

    def update_score(self, rows):
        """
        Update the score based on the number of rows cleared:
        - 1 row = 50 points
        - 2 rows = 100 * 1.5 = 150 points
        - 3 rows = 150 * 2 = 300 points
        - 4 rows = 200 * 3 = 600 points
        """
        if rows == 1:
            self.score += 50
        elif rows == 2:
            self.score += 150
        elif rows == 3:
            self.score += 300
        elif rows == 4:
            self.score += 600
        print(f"Score updated: {self.score}")
    
    def show_pause_menu(self):
        """Display the pause menu with the current score."""
        font = pygame.font.Font(None, 48)
        pause_text = ["Game Paused", f"Score: {self.score}", "Press P to Resume"]
    
        # Fill the screen with a black background
        self.screen.fill(BLACK)
        padding = 20
    
        # Render and display each line of the pause menu
        for i, line in enumerate(pause_text):
            text_surface = font.render(line, True, WHITE)
            rect = text_surface.get_rect(center=(self.screenWidth // 2, self.screenHeight // 2 + i * (font.get_linesize() + padding)))
            self.screen.blit(text_surface, rect)
    
        pygame.display.flip()
    
        # Pause the game and wait for "P" to resume
        paused = True
        while paused:
            for event in pygame.event.get():
                print(f"Paused Event: {event}")  # Debug events during pause
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Resume game on "P"
                        print("P key detected, resuming game.")
                        paused = False
    


    def pause_game(self):
        """Pause the game and wait for the user to resume or quit."""
        font = pygame.font.Font(None, 48)
        pause_text = ["Pause", "q: Quit", "Esc: Resume"]

        # Clear the screen and display a background for the pause text
        self.screen.fill(BLACK)
        padding = 10

        # Render each line of the message
        for i, line in enumerate(pause_text):
            pause_surface = font.render(line, True, WHITE)
            rect = pause_surface.get_rect(center=(self.screenWidth // 2, self.screenHeight // 2 + i * (font.get_linesize() + padding)))
            self.screen.blit(pause_surface, rect)

        pygame.display.flip()

        # Wait for the user to resume or quit
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Resume
                        paused = False
                    elif event.key == pygame.K_q:  # Quit
                        pygame.quit()
                        exit()



    def run_no_visual(self):
        if self.ai is None:
            return -1
        while True:
            x, piece = self.ai.get_best_move(self.board, self.curr_piece)

            # Simulate the move to check if it completes a line
            temp_board = deepcopy(self.board)
            y = temp_board.drop_height(piece, x)
            temp_board.place(x, y, piece)
            will_complete_line = any(width == temp_board.width for width in temp_board.widths)

            # Before dropping the piece, ask the user
            print(f"The AI has chosen to drop the piece at column {x}.")
            if will_complete_line:
                print("This move will complete a line.")
            user_input = input("Do you want to proceed with this move? (y/n): ").strip().lower()
            while user_input not in ['y', 'n']:
                user_input = input("Invalid input. Do you want to proceed with this move? (y/n): ").strip().lower()

            if user_input == 'n':
                print("AI will try a different move.")
                # Find an alternative move
                alternative_found = False
                for _ in range(3):  # Limit retries to avoid infinite loops
                    x, piece = self.ai.get_best_move(self.board, self.curr_piece)
                    temp_board = deepcopy(self.board)
                    y = temp_board.drop_height(piece, x)
                    temp_board.place(x, y, piece)
                    will_complete_line = any(width == temp_board.width for width in temp_board.widths)
                    if not will_complete_line:
                        alternative_found = True
                        break
                if not alternative_found:
                    print("No alternative moves available.")
                    break

            # Drop the piece with the chosen move
            self.curr_piece = piece
            y = self.board.drop_height(self.curr_piece, x)
            self.drop(y, x=x)
            if self.board.top_filled():
                break
        print(self.pieces_dropped, self.rows_cleared)
        return self.pieces_dropped, self.rows_cleared

    def run(self):
        pygame.init()
        self.screenSize = self.screenWidth, self.screenHeight
        self.pieceHeight = (self.screenHeight - self.top) / self.board.height
        self.pieceWidth = self.screenWidth / self.board.width
        self.screen = pygame.display.set_mode(self.screenSize)
        running = True
        if self.ai != None:
            MOVEEVENT, t = pygame.USEREVENT + 1, 100
        else:
            MOVEEVENT, t = pygame.USEREVENT + 1, 500
        pygame.time.set_timer(MOVEEVENT, t)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.QUIT:
                    running = False
                if self.ai != None:
                    if event.type == MOVEEVENT:
                        # if event.type == pygame.KEYDOWN:
                        x, piece = self.ai.get_best_move(self.board, self.curr_piece)
                        self.curr_piece = piece

                        while self.x != x:
                            if self.x - x < 0:
                                self.x += 1
                            else:
                                self.x -= 1
                            self.y -= 1
                            self.screen.fill(BLACK)
                            self.draw()
                            pygame.display.flip()
                            sleep(0.01)

                        y = self.board.drop_height(self.curr_piece, x)
                        while self.y != y:
                            self.y -= 1
                            self.screen.fill(BLACK)
                            self.draw()
                            pygame.display.flip()
                            sleep(0.01)

                        self.drop(y, x=x)
                        if self.board.top_filled():
                            running = False
                            break
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Pause the game
                        self.pause_game()
                    if event.key == pygame.K_p:  # Pause menu
                        self.show_pause_menu()
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        y = self.board.drop_height(self.curr_piece, self.x)
                        self.drop(y)
                        if self.board.top_filled():
                            running = False
                            break
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        if self.x - 1 >= 0:
                            occupied = False
                            for b in self.curr_piece.body:
                                if self.y + b[1] >= self.board.width:
                                    continue
                                if self.board.board[self.y + b[1]][self.x + b[0] - 1]:
                                    occupied = True
                                    break
                            if not occupied:
                                self.x -= 1
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        if self.x + 1 <= self.board.width - len(self.curr_piece.skirt):
                            occupied = False
                            for b in self.curr_piece.body:
                                if self.y + b[1] >= self.board.width:
                                    continue
                                if self.board.board[self.y + b[1]][self.x + b[0] + 1]:
                                    occupied = True
                                    break
                            if not occupied:
                                self.x += 1
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        rotated_piece = self.curr_piece.get_next_rotation()  # Get the rotated piece
                        if not self.has_collision(piece=rotated_piece, x=self.x, y=self.y):
                            # Only apply rotation if it doesn't result in a collision
                            self.curr_piece = rotated_piece
                        else:
                            print("Rotation blocked due to collision or boundary constraints.")
                if event.type == MOVEEVENT:
                    if self.board.drop_height(self.curr_piece, self.x) == self.y:
                        self.drop(self.y)
                        if self.board.top_filled():
                            running = False
                        break
                    self.y -= 1
            self.screen.fill(BLACK)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        # print("Game information:")
        print("Pieces dropped:", self.pieces_dropped)
        print("Rows cleared:", self.rows_cleared)
        return self.pieces_dropped, self.rows_cleared

    def evaluate_board(self, board):
        """
        A simple heuristic to evaluate the board state:
        - Penalize higher stack heights.
        - Penalize gaps below the highest blocks.
        """
        total_height = sum(max((row_idx for row_idx, cell in enumerate(col) if cell), default=0) for col in zip(*board.board))
        holes = sum(1 for col_idx, col in enumerate(zip(*board.board)) for row_idx, cell in enumerate(col) if not cell and any(col[:row_idx]))
        return -total_height - 2 * holes


    def drop(self, y, x=None):
        if x is None:
            x = self.x

        # Simulate placing the piece to check for potential line clears
        temp_board = deepcopy(self.board)
        temp_board.place(x, y, self.curr_piece)
        rows_to_clear = temp_board.widths.count(temp_board.width)

        if rows_to_clear > 0:
            self.display_row_completion_prompt(rows_to_clear)
            user_decision = self.get_user_decision()
            if user_decision == 'n':
                print("Switching to manual control for this piece.")
                self.manual_control()
                return  # Exit drop to prevent further automatic placement

        # Place the current piece on the board
        self.board.place(x, y, self.curr_piece)
        self.x = 5
        self.y = 20

        # Clear rows if necessary
        cleared_rows = self.board.clear_rows()
        if cleared_rows > 0:
            self.update_score(cleared_rows)  # Update the score dynamically
            self.rows_cleared += cleared_rows

        self.curr_piece = Piece()
        self.pieces_dropped += 1



    def display_row_completion_prompt(self, rows_to_clear):
        """Display a 'Yes/No' prompt with the number of rows to be completed."""
        font = pygame.font.Font(None, 36)
        prompt_text = f"Complete {rows_to_clear} row(s)? (Y/N)"
        prompt = font.render(prompt_text, True, BLACK, WHITE)  # Black text with white background
        rect = prompt.get_rect(center=(self.screenWidth // 2, self.screenHeight // 2))

        # Draw the background rectangle
        padding = 10
        background_rect = pygame.Rect(
            rect.left - padding, rect.top - padding,
            rect.width + 2 * padding, rect.height + 2 * padding
        )
        pygame.draw.rect(self.screen, WHITE, background_rect)

        # Draw the text on top of the rectangle
        self.screen.blit(prompt, rect)
        pygame.display.flip()

    

    def get_user_decision(self):
        """Wait for the user to press 'y' or 'n'."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        return 'y'
                    if event.key == pygame.K_n:
                        return 'n'

    def manual_control(self):
        """
        Allow the user to manually control the piece, holding it in suspension.
        Controls:
            - 'a' or LEFT: Move left
            - 'd' or RIGHT: Move right
            - 'w' or UP: Rotate
            - 's' or DOWN: Drop faster
            - SPACE: Drop instantly
        """
        print("Manual control activated. Use 'a' (left), 'd' (right), 'w' (rotate), 's' (faster drop), SPACE (instant drop).")

        # Reset the piece to the top
        self.curr_piece = Piece(body=self.curr_piece.body, color=self.curr_piece.color)  # Recreate the same piece
        self.x, self.y = 5, self.board.height - 1  # Reset to the top-middle of the board
        clock = pygame.time.Clock()  # Create a clock to manage frame rate
        drop_timer = 0  # Timer for automatic downward movement
        drop_interval = 500  # Interval for automatic drop in milliseconds
        running = True

        # Temporarily disable MOVEEVENT
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)

        while running:
            dt = clock.tick(30)  # Limit to 30 frames per second and get delta time
            drop_timer += dt  # Increment drop timer

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Pause the game
                        self.pause_game()
                    if event.key == pygame.K_p:
                        self.show_pause_menu()
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:  # Move left
                        if self.x > 0:
                            occupied = any(
                                self.board.board[self.y + b[1]][self.x + b[0] - 1]
                                for b in self.curr_piece.body
                                if self.y + b[1] < self.board.height
                            )
                            if not occupied:
                                self.x -= 1
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:  # Move right
                        if self.x < self.board.width - len(self.curr_piece.skirt):
                            occupied = any(
                                self.board.board[self.y + b[1]][self.x + b[0] + 1]
                                for b in self.curr_piece.body
                                if self.y + b[1] < self.board.height
                            )
                            if not occupied:
                                self.x += 1
                    elif event.key == pygame.K_w or event.key == pygame.K_UP:  # Rotate
                        rotated_piece = self.curr_piece.get_next_rotation()  # Get the rotated piece
                        if not self.has_collision(piece=rotated_piece, x=self.x, y=self.y):
                            # Only apply rotation if it doesn't result in a collision
                            self.curr_piece = rotated_piece
                        else:
                            print("Rotation blocked due to collision or boundary constraints.")
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:  # Faster drop
                        drop_interval = 50  # Increase drop speed for faster movement
                    elif event.key == pygame.K_SPACE:  # Instant drop
                        self.y = self.board.drop_height(self.curr_piece, self.x)  # Move directly to the bottom
                        self.board.place(self.x, self.y, self.curr_piece)  # Place the piece
                        print("Piece dropped instantly.")
                        self.rows_cleared += self.board.clear_rows()
                        self.curr_piece = Piece()  # Generate a new piece
                        self.pieces_dropped += 1
                        self.x, self.y = 5, self.board.height - 1
                        running = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:  # Reset speed
                        drop_interval = 500  # Reset to normal drop interval

            # Automatic downward movement
            if drop_timer >= drop_interval:
                self.y -= 1
                drop_timer = 0  # Reset the drop timer

                # Check for collision or landing
                if self.has_collision():
                    self.y += 1  # Reset to last valid position
                    self.board.place(self.x, self.y, self.curr_piece)
                    print("Piece manually placed.")
                    self.rows_cleared += self.board.clear_rows()
                    self.curr_piece = Piece()  # Generate a new piece
                    self.pieces_dropped += 1
                    self.x, self.y = 5, self.board.height - 1
                    running = False

            # Redraw the game state
            self.screen.fill(BLACK)
            self.draw()
            pygame.display.flip()

        # Re-enable MOVEEVENT after manual control ends
        pygame.time.set_timer(pygame.USEREVENT + 1, 100 if self.ai else 500)
    
    def has_collision(self, piece=None, x=None, y=None):
        """
        Check if the given piece at position (x, y) collides with the board or boundaries.
        Defaults to the current piece if no piece, x, or y is provided.
        """
        if piece is None:
            piece = self.curr_piece
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        for block in piece.body:
            bx, by = x + block[0], y + block[1]
            # Check boundaries
            if bx < 0 or bx >= self.board.width or by < 0 or by >= self.board.height:
                return True
            # Check collision with other blocks
            if self.board.board[by][bx]:
                return True
        return False    

    def get_critical_holes(self, board):
        """
        Identify the critical holes in rows that would lead to a row being completed.
        """
        critical_holes = set()
        for row_idx, width in enumerate(board.widths):
            if width == board.width - 1:  # Row is one block short of completion
                for col_idx, filled in enumerate(board.board[row_idx]):
                    if not filled:  # Add the hole position
                        critical_holes.add((col_idx, self.board.height - row_idx - 1))
        return critical_holes


    def fills_critical_holes(self, board, piece, x, y, critical_holes):
        """
        Check if placing the piece at (x, y) fills more than one critical hole.
        Allow one critical hole to remain.
        """
        holes_filled = 0
        for block in piece.body:
            bx, by = x + block[0], y + block[1]
            if (bx, by) in critical_holes:
                holes_filled += 1
    
        # Return True if more than one critical hole is filled
        return holes_filled > 1


    def draw(self):
        self.draw_pieces()
        self.draw_hover()
        self.draw_grid()


    def draw_grid(self):
        for row in range(0, self.board.height):
            start = (0, row * self.pieceHeight + self.top)
            end = (self.screenWidth, row * self.pieceHeight + self.top)
            pygame.draw.line(self.screen, WHITE, start, end, width=2)
        for col in range(1, self.board.height):
            start = (col * self.pieceWidth, self.top)
            end = (col * self.pieceWidth, self.screenHeight)
            pygame.draw.line(self.screen, WHITE, start, end, width=2)
        # border
        tl = (0, 0)
        bl = (0, self.screenHeight - 2)
        br = (self.screenWidth - 2, self.screenHeight - 2)
        tr = (self.screenWidth - 2, 0)
        pygame.draw.line(self.screen, WHITE, tl, tr, width=2)
        pygame.draw.line(self.screen, WHITE, tr, br, width=2)
        pygame.draw.line(self.screen, WHITE, br, bl, width=2)
        pygame.draw.line(self.screen, WHITE, tl, bl, width=2)


    def draw_pieces(self):
        for row in range(self.board.height):
            for col in range(self.board.width):
                if self.board.board[row][col]:
                    tl = (
                        col * self.pieceWidth,
                        (self.board.height - row - 1) * self.pieceHeight,
                    )
                    pygame.draw.rect(
                        self.screen,
                        self.board.colors[row][col],
                        pygame.Rect(tl, (self.pieceWidth, self.pieceHeight)),
                    )

    def draw_hover(self):
        for b in self.curr_piece.body:
            tl = (
                (self.x + b[0]) * self.pieceWidth,
                (self.board.height - (self.y + b[1]) - 1) * self.pieceHeight,
            )
            pygame.draw.rect(
                self.screen,
                self.curr_piece.color,
                pygame.Rect(tl, (self.pieceWidth, self.pieceHeight)),
            )
