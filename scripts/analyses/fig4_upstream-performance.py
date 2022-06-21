#!/usr/bin/env python3
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(
    context='paper',
    style="ticks",
    rc={
        "axes.spines.right": False,
        "axes.spines.top": False
    }
)


def fig_upstream_performance(config=None) -> None:

    if config is None:
        config = vars(get_args().parse_args())

    os.makedirs(config['figures_dir'], exist_ok=True)

    fig, fig_axs = plt.subplot_mosaic(
        """
        ABCD
        """,
        figsize=(10, 2),
    )

    training_styles = ['autoencoder', 'CSM', 'BERT', 'NetBERT']
    for i, (training_style, ax, loss_label, name) in enumerate(
        zip(
                training_styles,
                [fig_axs['A'], fig_axs['B'], fig_axs['C'], fig_axs['D']],
                [r'$L_{rec}$', r'$L_{rec}$', r'$L_{rec} + L_{cls}$', r'$L_{rec} + L_{cls}$'],
                ['Autoencoding', 'CSM', 'Seq-BERT', 'Net-BERT']
            )
        ):
        upstream_model_dir = [
            p for p in 
            os.listdir(config['upstream_models_dir'])
            if f'train-{training_style}' in p
            and 'warmup' not in p
            and 'Pretrained' not in p
        ]
        assert len(upstream_model_dir) == 1, \
            f'{training_style} should have exactly one path in ' +\
            f'{config["upstream_models_dir"]}'
        upstream_model_dir = upstream_model_dir[0]
        upstream_model_dir = os.path.join(
            config['upstream_models_dir'],
            upstream_model_dir
        )
        train_history = pd.read_csv(
            os.path.join(
                upstream_model_dir,
                'train_history.csv'
            )
        )
        eval_history = pd.read_csv(
            os.path.join(
                upstream_model_dir,
                'eval_history.csv'
            )
        )
        ax.plot(
            eval_history['step'].values,
            eval_history['loss'].values,
            label='Eval.' if i==0 else None,
            color='k',
            linestyle='solid',
            lw=2
        )
        ax.plot(
            train_history['step'].values[1:-1], # exclude 0th and final step
            train_history['loss'].values[1:-1],
            label='Train' if i==0 else None,
            color='k',
            linestyle='dashed',
            lw=1
        )
        ax.set_title(f"{name}")
        ax.set_xlabel('Training steps')
        ax.set_xticks((10000, 50000, 100000, 150000, 200000, 250000, 300000))
        ax.set_xticklabels((10000, '', '', '150000', '', '', 300000))
        ax.set_ylabel(f"Loss ({loss_label})")
        if i == 0:
            ax.legend(
                ncol=1,
                fontsize=8
            )
    
    fig.tight_layout()
    fig.savefig(
        os.path.join(
            config['figures_dir'],
            'fig4_upstream-performance.png'
        ),
        dpi=600
    )

    return None


def get_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='figure hyperopt')

    parser.add_argument(
        '--upstream-models-dir',
        metavar='DIR',
        default='results/models/hyperopt/',
        type=str,
        help=''
    )
    parser.add_argument(
        '--figures-dir',
        metavar='DIR',
        default='results/figures/',
        type=str,
        help=''
    )

    return parser


if __name__ == '__main__':
    fig_upstream_performance()