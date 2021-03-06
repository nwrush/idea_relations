# Nikko Rush
# 6/20/2017

import datetime

import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
import pickle

import data
import idea_relations_runner as li


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


def plot_things(articles, num_ideas, cooccur_func=None, group_by="years", start_time=1980, end_time=2016):
    # Lifted from item_relations:generate_scatter_dist_plot
    articles = filter_articles(articles, start_time, end_time)

    result = li.get_count_cooccur(articles, func=cooccur_func)
    pmi = li.get_pmi(result["cooccur"], result["count"],
                     float(result["articles"]), num_ideas=num_ideas)
    articles_group = li.get_time_grouped_articles(articles, group_by=group_by, start_time=start_time, end_time=end_time)
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

    time_steps = sorted(articles_group.keys())

    return pmi, ts_correlation, ts_matrix, time_steps


def filter_articles(articles, start_time, end_time, default_date=datetime.datetime(1, 1, 1)):
    if not isinstance(start_time, datetime.datetime):
        start_time = dateutil.parser.parse(str(start_time), default=default_date)
    if not isinstance(end_time, datetime.datetime):
        end_time = dateutil.parser.parse(str(end_time), default=default_date)

    return [article for article in articles if start_time <= article.fulldate <= end_time]


def get_output(args, articles, idea_names, cooccur_func=None, name=None, group_by="years", start_time=1980,
               end_time=2016):
    pmi, ts_correlation, ts_matrix, time_values = plot_things(articles, len(idea_names), cooccur_func, group_by,
                                                              start_time, end_time)

    return data.Data(args=args, pmi_matrix=pmi, ts_correlation_matrix=ts_correlation, ts_matrix=ts_matrix,
                     idea_names=idea_names, x_vals=time_values, name=name)


if __name__ == "__main__":
    main()
