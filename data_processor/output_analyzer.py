# Nikko Rush
# 6/20/2017

import pickle

import numpy as np
import matplotlib.pyplot as plt

import idea_relations as li

def reverse_dict(input):
    output = dict()
    for key, value in input.items():
        if value in output:
            print("Warning: Duplicate key will be overwritten in new dictionary")
        output[value] = key
    return output

def is_square(a):
    row, col = a.shape
    return row == col

class Data():

    def __init__(self, pmi_matrix=None, ts_correlation_matrix=None, ts_matrix=None, idea_names=None, x_vals=None):
        self.pmi = pmi_matrix
        self.ts_correlation = ts_correlation_matrix
        self.ts_matrix = ts_matrix
        self.idea_names = idea_names
        self.x_values = x_vals

        self.idea_numbers = reverse_dict(self.idea_names)
        self.num_ideas = len(self.idea_names)

        self.strength_matrix = self._get_strength_matrix()

        self.relation_types = ("Friends", "Tryst", "Head-To-Head", "Arms-Race") # Layout the relation in quadrant order
        pass

    def _get_strength_matrix(self):
        assert self.pmi.shape == self.ts_correlation.shape
        assert is_square(self.pmi)

        a = np.multiply(self.pmi, self.ts_correlation)

        lower_indexes = np.tril_indices(self.pmi.shape[0])
        a[lower_indexes] = np.nan
        return a

    def get_idea_names(self, indexes):
        if isinstance(indexes, int):
            return self.idea_names[indexes]

        try:
            names = list()
            for index in indexes:
                names.append(self.idea_names[index])
            return names
        except TypeError as err:
            print(err)

        return None


def reverse_dictionary(input):
    output = dict()
    for key, value in input.items():
        if value in output.keys():
            print("Warning: Duplicate key in new dictionary. Will be overwritten")
        output[value] = key
    return output

def main():
    ts_matrix, idea_names, type_list = pickle.load(open('data.p', 'rb'))

    reverse_idea_names = reverse_dictionary(idea_names)

    grammar_index = reverse_idea_names['grammar']

    grammar_ts = ts_matrix[grammar_index]

    x_values = list(range(ts_matrix.shape[1]))

    x_tick_labels = [i for i in range(1980, 2015)]

    fig, ax = plt.subplots()
    fig.canvas.draw()

    ax.plot(x_values, grammar_ts)
    ax.set_xticks(np.arange(35))
    ax.set_xticklabels(x_tick_labels, rotation=45)
    plt.show()

def retrieve_data(articles, num_ideas, cooccur_func=None, group_by="years"):
    result = li.get_count_cooccur(articles, func=cooccur_func)
    pmi = li.get_pmi(result["cooccur"], result["count"],
                  float(result["articles"]), num_ideas=num_ideas)
    articles_group = li.get_time_grouped_articles(articles, group_by=group_by)
    info_dict = {k: li.get_count_cooccur(articles_group[k], func=cooccur_func)
                 for k in articles_group}
    ts_correlation = li.get_ts_correlation(info_dict, num_ideas,
                                        normalize=True)

    xs, ys = [], []
    for i in range(num_ideas):
        for j in range(i + 1, num_ideas):
            if np.isnan(pmi[i, j]) or np.isnan(ts_correlation[i, j]):
                continue
            if np.isinf(pmi[i, j]) or np.isinf(ts_correlation[i, j]):
                continue
            xs.append(ts_correlation[i, j])
            ys.append(pmi[i, j])

    plt.scatter(xs, ys)
    plt.savefig("pmi_corr_plot.png")

    ts_matrix = li.get_time_series(info_dict, num_ideas, normalize=True)

    return (pmi, ts_correlation, ts_matrix)

def time_series(info_dict, num_ideas, normalize=True):
    return li.get_time_series(info_dict, num_ideas, normalize)


def plot_things(articles, num_ideas, cooccur_func=None, group_by="years"):
  
    # Lifted from item_relations:generate_scatter_dist_plot
    result = li.get_count_cooccur(articles, func=cooccur_func)
    pmi = li.get_pmi(result["cooccur"], result["count"],
                  float(result["articles"]), num_ideas=num_ideas)
    articles_group = li.get_time_grouped_articles(articles, group_by=group_by)
    info_dict = {k: li.get_count_cooccur(articles_group[k], func=cooccur_func)
                 for k in articles_group}
    ts_correlation = li.get_ts_correlation(info_dict, num_ideas,
                                        normalize=True)

    xs, ys = [], []
    for i in range(num_ideas):
        for j in range(i + 1, num_ideas):
            if np.isnan(pmi[i, j]) or np.isnan(ts_correlation[i, j]):
                continue
            if np.isinf(pmi[i, j]) or np.isinf(ts_correlation[i, j]):
                continue
            xs.append(ts_correlation[i, j])
            ys.append(pmi[i, j])

    plt.scatter(xs, ys)
    plt.savefig("pmi_corr_plot.png")

    ts_matrix = li.get_time_series(info_dict, num_ideas, normalize=True)

    return (pmi, ts_correlation, ts_matrix)
    
def get_output(articles, idea_names, cooccur_func=None, group_by="years"):
    pmi, ts_correlation, ts_matrix = plot_things(articles, len(idea_names), cooccur_func, group_by)

    return Data(pmi_matrix=pmi, ts_correlation_matrix=ts_correlation, ts_matrix=ts_matrix, idea_names=idea_names)

if __name__ == "__main__":
    main()
