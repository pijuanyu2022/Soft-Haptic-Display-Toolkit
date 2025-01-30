import time

class TactileArrayController:
    def __init__(self, queue):
        """
        Initialize the Tactile Array Controller.

        Args:
            queue: Queue for sending actuator commands to the GUI.
        """
        self.queue = queue
        self.b_string = "0" * 16  # Initial binary string (all valves off)
    
    def matrix_to_binary_string(self, matrix):
        """
        Convert a 4x4 matrix to a 16-bit binary string.

        Args:
            matrix (list of list): 4x4 matrix representing the tactile pattern.

        Returns:
            str: 16-bit binary string.
        """
        binary_string = ''.join(str(cell) for row in matrix for cell in row)
        return binary_string

    def apply_pattern(self, matrix):
        """
        Apply a tactile pattern based on a 4x4 matrix.

        Args:
            matrix (list of list): 4x4 matrix representing the tactile pattern.
        """
        self.b_string = self.matrix_to_binary_string(matrix)
        self.queue.put(("Valve", self.b_string))
        print(f"Pattern applied: {self.b_string}")
    
    def clear_pattern(self):
        """clear the pattern"""
        pattern = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        self.apply_pattern(pattern)

    def test_pattern(self):
        """test the pattern"""
        pattern = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
        ]
        self.apply_pattern(pattern)

    def static_1(self):
        """Pattern for 1.png"""
        pattern = [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
        ]
        self.apply_pattern(pattern)

    def static_2(self):
        """Pattern for 2.png"""
        pattern = [
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 1, 1, 1],
            [1, 0, 0, 1],
        ]
        self.apply_pattern(pattern)

    def static_3(self):
        """Pattern for 3.png"""
        pattern = [
            [0, 1, 1, 1],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 1, 1],
        ]
        self.apply_pattern(pattern)
    
    def static_4(self):
        """Pattern for 4.png"""
        pattern = [
            [0, 1, 0, 0],
            [1, 1, 1, 1],
            [0, 1, 0, 0],
            [0, 1, 0, 0],
        ]
        self.apply_pattern(pattern)
    
    def static_5(self):
        """Pattern for 5.png"""
        pattern = [
            [1, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 0],
        ]
        self.apply_pattern(pattern)
    
    def static_6(self):
        """Pattern for 6.png"""
        pattern = [
            [1, 0, 0, 1],
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
        ]
        self.apply_pattern(pattern)
    
    def static_7(self):
        """Pattern for 7.png"""
        pattern = [
            [1, 0, 1, 0],
            [1, 0, 1, 0],
            [1, 0, 1, 0],
            [1, 0, 1, 0],
        ]
        self.apply_pattern(pattern)
    
    def static_8(self):
        """Pattern for 8.png"""
        pattern = [
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 1, 1, 1],
        ]
        self.apply_pattern(pattern)
    
    def static_9(self):
        """Pattern for 9.png"""
        pattern = [
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1],
        ]
        self.apply_pattern(pattern)

    def static_10(self):
        """Pattern for 10.png"""
        pattern = [
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1],
            [1, 0, 0, 0],
        ]
        self.apply_pattern(pattern)
    
    def static_11(self):
        """Pattern for 11.png"""
        pattern = [
            [1, 1, 1, 1],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
        ]
        self.apply_pattern(pattern)

    def static_12(self):
        """Pattern for 12.png"""
        pattern = [
            [1, 0, 0, 1],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1],
        ]
        self.apply_pattern(pattern)
    


    def animation_1(self):
        """
        Animation pattern for 1.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_1")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 1 complete.")
    

    def animation_2(self):
        """
        Animation pattern for 2.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_2")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 2 complete.")

    
    def animation_3(self):
        """
        Animation pattern for 3.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_3")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 3 complete.")
    

    def animation_4(self):
        """
        Animation pattern for 4.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_4")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 4 complete.")


    def animation_5(self):
        """
        Animation pattern for 5.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_5")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 5 complete.")


    def animation_6(self):
        """
        Animation pattern for 6.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_6")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 6 complete.")
    
    def animation_7(self):
        """
        Animation pattern for 7.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 1, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
            ],
            [
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 1, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 1, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_7")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.05)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 7 complete.")
    

    def animation_8(self):
        """
        Animation pattern for 8.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 1, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 1, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
            ],
            [
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 1, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 1, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 1, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_8")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.05)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 8 complete.")

    
    def animation_9(self):
        """
        Animation pattern for 9.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
            ],
            [
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_9")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.15)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 9 complete.")

    def animation_10(self):
        """
        Animation pattern for 10.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
            ],
            [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_10")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.15)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 10 complete.")

    def animation_11(self):
        """
        Animation pattern for 11.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [1, 0, 0, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 0, 0, 1],
            ],
            [
                [0, 1, 1, 0],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_11")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 11 complete.")
    
    def animation_12(self):
        """
        Animation pattern for 12.png in the 'Animation' folder.
        Repeats the sequence 3 times with a 0.5s delay between repetitions.
        """
        # Define the animation sequence
        animation_sequence = [
            [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 1, 0],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 1, 0],
            ],
            [
                [1, 0, 0, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 0, 0, 1],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        ]

        # Repeat the animation sequence 3 times
        for repeat in range(3):
            print(f"Starting repetition {repeat + 1} of animation_12")
            for step in animation_sequence:
                self.apply_pattern(step)
                time.sleep(0.1)  # Wait for 0.1 seconds between steps
            time.sleep(0.5)  # Wait for 0.5 seconds between repetitions

        print("Animation 12 complete.")


    def update_binary_string(self, indices, state):
        """
        Update the binary string for the tactile array.

        Args:
            indices (list): List of indices (1-16) to update.
            state (str): "1" to turn ON, "0" to turn OFF.
        """
        b_list = list(self.b_string)
        for index in indices:
            if 1 <= index <= 16:  # Ensure indices are within range
                b_list[index - 1] = state
        self.b_string = ''.join(b_list)

    def send_binary_string(self):
        """Send the current binary string to the actuator queue."""
        self.queue.put(("Valve", self.b_string))
        print(f"Sent binary string: {self.b_string}")

    def demo_1(self):
        """Run Demo 1: Spiral sequence."""
        spiral_sequence = [1, 5, 9, 13, 14, 15, 16, 12, 8, 4, 3, 2, 6, 10, 11, 7]
        print("Starting Demo 1: Spiral sequence")
        for index in spiral_sequence:
            self.update_binary_string([index], "1")
            self.send_binary_string()
            time.sleep(0.15)
            self.update_binary_string([index], "0")  # Turn off the valve

    def demo_2(self):
        """Run Demo 2: Row-by-row activation."""
        print("Starting Demo 2: Row-by-row")
        for row in range(4):  # 4 rows
            indices = [row * 4 + i + 1 for i in range(4)]
            self.update_binary_string(indices, "1")
            self.send_binary_string()
            time.sleep(0.5)
            self.update_binary_string(indices, "0")  # Turn off the row

    def demo_3(self):
        """Run Demo 3: Left-to-right and reverse."""
        print("Starting Demo 3: Left-to-right and reverse")
        sequence = list(range(1, 17)) + list(range(16, 0, -1))
        for index in sequence:
            self.update_binary_string([index], "1")
            self.send_binary_string()
            time.sleep(0.1)
            self.update_binary_string([index], "0")  # Turn off the valve

    def demo_4(self):
        """Run Demo 4: Right-to-left."""
        print("Starting Demo 4: Right-to-left")
        for col in range(4):  # 4 columns
            indices = [col + 1 + i * 4 for i in range(4)]
            self.update_binary_string(indices, "1")
            self.send_binary_string()
            time.sleep(0.5)
            self.update_binary_string(indices, "0")  # Turn off the column
