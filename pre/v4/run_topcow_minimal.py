from train import Pix2PixTrainer


if __name__ == "__main__":
    trainer = Pix2PixTrainer(data_folder="./gan_train")
    trainer.train(epochs=1, batch_size=1, validation_split=0.25)
