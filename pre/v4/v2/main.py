import argparse
from v4.v2.train import Pix2PixTrainer
from v4.v2.inference import MRIInterpolator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, required=True, choices=['train', 'inference'])
    parser.add_argument('--model_path', type=str, default='./checkpoints/pix2pix_epoch_final.pth')
    parser.add_argument('--input_folder', type=str, default='./gan_inputs')
    parser.add_argument('--output_folder', type=str, default='./gan_outputs')
    parser.add_argument('--train_folder', type=str, default='./gan_train')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        trainer = Pix2PixTrainer(data_folder=args.train_folder)
        trainer.train(epochs=100, batch_size=8)
    
    elif args.mode == 'inference':
        interpolator = MRIInterpolator(args.model_path)
        interpolator.process_folder(args.input_folder, args.output_folder)

if __name__ == "__main__":
    main()