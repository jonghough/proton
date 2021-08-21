class LearnerParams:

    def __init__(self, is_training, eps_min, eps_max, eps_decay_steps, n_steps, 
                start_training_steps, training_interval,
                save_steps, copy_steps, discount_rate, learning_rate, 
                model_path, batch_size):
   
        self.is_training = is_training
        self.eps_min = eps_min
        self.eps_max = eps_max
        self.eps_decay_steps = eps_decay_steps
        self.n_steps = n_steps
        self.start_training_steps = start_training_steps
        self.training_interval = training_interval
        self.save_steps = save_steps
        self.copy_steps = copy_steps
        self.discount_rate = discount_rate 
        self.learning_rate = learning_rate
        self.model_path = model_path
        self.batch_size = batch_size