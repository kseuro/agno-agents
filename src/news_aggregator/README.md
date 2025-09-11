# News Aggregator

Creates a two Agent workflow that searches the web for news related to user keyword inputs and writes a digest file containing a meta-analysis of news and topics related to the query.

This projects demonstates how Agents can interact with external tools and personalize experiences for users by leveraging `agno`'s built in [search](https://docs.agno.com/tools/toolkits/search/arxiv) tools.

## Usage

### With Command Line Arguments

Run this workflow with command line arguments:

```shell
pixi run python main.py -k programming -k agents -k 'agno framework' -n 5
```

This will search for 5 articles related to the supplied keywords.

### With Interactive Prompt

```shell
pixi run python main.py
```
