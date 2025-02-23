"""
multi_absolute.py
====================================
Module to plot multiple absolute spectra.
"""

import matplotlib.pyplot as plt

from .plotter import Plotter


class MultiAbsolutePlotter(Plotter):

    def __plot_multi_absolute(self):
        spectra_class = self.spectra_class
        spectra_df = self.spectra
        fig, ax = plt.subplots(figsize=(16, 9))
        for spectrum in spectra_df.to_dict('records'):
            x, y, e = self._get_inputs(spectrum)
            ax.plot(x, y, lw=2, alpha=0.95, label=spectrum['source_id'])
        ax.set_xlabel(spectra_class.get_position_label())
        ax.set_ylabel(spectra_class.get_flux_label())
        fig.tight_layout()
        if self.legend:
            by_label = dict()
            for ax in fig.axes:
                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
            fig.subplots_adjust(top=0.95, bottom=0.05, left=0.05, right=0.85, wspace=0.020)
            fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=1.0)
        return fig, ax

    def plot_fig(self):
        n_spectra = len(self.spectra)
        if self.show_plot and self.legend and n_spectra > self.max_spectra_on_multi:
            raise ValueError(f'The legend can only be shown for a list of spectra no longer than '
                             f'{self.max_spectra_on_multi} elements. Try setting legend to False or retry with a '
                             f'shorter list.')
        self.__plot_multi_absolute()
        if self.save_file:
            self._save_figure()
        if self.show_plot:
            plt.show()
        plt.close()
