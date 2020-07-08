# Exploring spatio-temporal soccer events using public event data

<img width=200, src="https://raw.githubusercontent.com/scikit-mobility/tutorials/master/AMLD%202020/sobigdata_logo.jpg" />

Tutorial supported by EU project <a href="https://cordis.europa.eu/project/id/871042">SoBigData++</a> RI (Grant Agreement 871042).

A video version of the tutorial is available on YouTube at:
- https://www.youtube.com/watch?v=ZXEHPKmx410&t=430s (Luca Pappalardo)
- https://www.youtube.com/watch?v=TCyahs5HRMM (Paolo Cintia)

The code has been developed by:
- Luca Pappalardo, National Research Council of Italy (CNR), luca.pappalardo@isti.cnr.it
- Alessio Rossi, University of Pisa, alessio.rossi2@gmail.com
- Paolo Cintia, University of Pisa, paolo.cintia@di.unipi.it

and explores the events in an open collection of soccer-logs described in the following paper (please cite it if you use the public data of the code in this folder):

<a id='datapaper'></a>
- (PCR2019) Pappalardo, L., Cintia, P., Rossi, A. et al. **A public data set of spatio-temporal match events in soccer competitions**. Nature Scientific Data 6, 236 (2019). https://doi.org/10.1038/s41597-019-0247-7

## Data collection
The soccer-logs have been collected and provided by <a href="https://wyscout.com/">Wyscout</a>. The procedure of data collection is performed by expert video analysts (the operators), who are trained and focused on data collection for soccer, through a proprietary software (the tagger). The tagger has been developed and improved over several years and it is constantly updated to always guarantee better and better performance at the highest standards. 

Based on the tagger and the videos of soccer games, to guarantee the accuracy of data collection, the tagging of events in a match is performed by three operators, one operator per team and one operator acting as responsible supervisor of the output of the whole match. Optionally for near-live data delivery a team of four operators is used, one of them acting to speed up the collection of complex events which need additional and specific attributes or a quick review. 
<a id='datapaper'></a>
Further details on data collection can be found in the data paper ([PCR2019](#datapaper)).

## Data Records
The data sets are released under the CC BY 4.0 License and are publicly available on figshare:

- Pappalardo, Luca; Massucco, Emanuele (2019): **Soccer match event dataset**. figshare. Collection. https://doi.org/10.6084/m9.figshare.c.4415000.v5

The data refer to season 2017/2018 of five national soccer competitions in Europe: Spanish first division, Italian first division, English first division, German first division, French first division. In addition, there are data about the World cup 2018 and the European cup 2016, which are competitions for national teams. In total, we provide seven data sets corresponding to information about all competitions, matches, teams, players, events, referees and coaches. 

Each data set is provided in JSON format (JavaScript Object Notation). The following table shows the list of competitions we make available with their total number of matches, events and players. The data covers a total of around 1,941 matches, 3,251,294 events and 4,299 players.
  
| Competition            | #matches | #events   | #players |
|------------------------|----------|-----------|----------|
| Spanish first division | 380      | 628,659   | 619      |
| English first division | 380      | 643,150   | 603      |
| Italian first division | 380      | 647,372   | 686      |
| German first division  | 306      | 519,407   | 537      |
| French first division  | 380      | 632,807   | 629      |
| World cup 2018         | 64       | 101,759   | 736      |
| European cup 2016      | 51       | 78,140    | 552      |
|                        | 1,941    | 3,251,294 | 4,299    |


## Outline of the tutorial
- Import libraries
- Load public datasets
- How are the data collected?
- Structure of data
  - Players
  - Competitions
  - Matches
  - Events
- Basic statistics on events
  - Frequency of events by type
  - Distribution of number of events per match
  - Plot events on the field
    - Static plot
    - Interactive plot
- Spatial distribution of events
- Intra-match evolution
- Advanced statistics
  - Passing networks
  - Flow centrality
  - PlayeRank algorithm
 
