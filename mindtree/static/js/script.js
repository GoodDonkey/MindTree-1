// 단순 변수만 선언해서 Array 타입의 데이터로 만들면
// 아래 차트의 data에 넣으면 된다.
let sentiment2 = sentimentJson.document.confidence
console.log(sentiment2)
let sentimentArray = Object.values(sentiment2)
console.log(sentimentArray)

let negative_ratio = sentimentJson.document.confidence.negative
let neutral_ratio = sentimentJson.document.confidence.neutral
let positive_ratio = sentimentJson.document.confidence.positive


// bar chart
new Chart(document.getElementById("bar-chart"), {
    type: 'bar',
    data: {
        labels: ["Negative", "Neutral", "Positive"],
        datasets: [
            {
                label: "Sentiment",
                backgroundColor: ["#ff5959", "#b0b0b0", "#59ff64"],
                data: sentimentArray
            }
        ]
    },
    options: {
        responsive: false,
        legend: {
            position: 'top',
            display: false
        },
        title: {
            display: true,
            text: 'your sentiment statement'
        }
    }
});

//doughnut chart
new Chart(document.getElementById("doughnut-chart"), {
    type: 'doughnut',
    data: {
        labels: ["Negative", "Neutral", "Positive"],
        datasets: [
            {
                label: "Sentiment",
                backgroundColor: ["#ff5959", "#b0b0b0", "#59ff64"],
                data: sentimentArray
            }
        ]
    },
    options: {
        responsive: false,
        title: {
            display: true,
            text: 'your sentiment statement'
        }
    }
});

// radar chart
// new Chart(document.getElementById("radar-chart"), {
//     type: 'radar',
//     data: {
//         labels: ["Negative", "Neutral", "Positive"],
//         datasets: [
//             {
//                 label: "Sentiment",
//                 fill: true,
//                 backgroundColor: "rgba(179,181,198,0.2)",
//                 borderColor: "rgba(179,181,198,1)",
//                 pointBorderColor: "#fff",
//                 pointBackgroundColor: "rgba(179,181,198,1)",
//                 data: sentimentArray
//             }
//         ]
//     },
//     options: {
//         responsive: false,
//         title: {
//             display: true,
//             text: 'your sentiment statement'
//         },
//         scale: {
//             ticks: {
//                 display: true,
//                 beginAtZero: true,
//                 max: 1
//             }
//         }
//     }
// });


//horizonal stacked bar chrart
//horizonal stacked bar chart options
// var barOptions_stacked = {
//     tooltips: {
//         enabled: false
//     },
//     hover: {
//         animationDuration: 0
//     },
//     scales: {
//         xAxes: [{
//             scaleLabel: {
//                 display: false
//             },
//             gridLines: {
//             },
//             stacked: true
//         }],
//         yAxes: [{
//             gridLines: {
//                 display: false,
//                 color: "#fff",
//                 zeroLineColor: "#fff",
//                 zeroLineWidth: 0
//             },
//
//             stacked: true
//         }]
//     },
//     legend: {
//         display: false
//     },
//
//     animation: {
//         onComplete: function () {
//             var chartInstance = this.chart;
//             var ctx = chartInstance.ctx;
//             ctx.textAlign = "left";
//             ctx.font = "9px Open Sans";
//             ctx.fillStyle = "#fff";
//
//             Chart.helpers.each(this.data.datasets.forEach(function (dataset, i) {
//                 var meta = chartInstance.controller.getDatasetMeta(i);
//                 Chart.helpers.each(meta.data.forEach(function (bar, index) {
//                     data = dataset.data[index];
//                     if (i == 0) {
//                         ctx.fillText(data, 50, bar._model.y + 4);
//                     } else {
//                         ctx.fillText(data, bar._model.x - 25, bar._model.y + 4);
//                     }
//                 }), this)
//             }), this);
//         }
//     },
//     pointLabelFontFamily: "Quadon Extra Bold",
//     scaleFontFamily: "Quadon Extra Bold",
// };

//horizontal stacked bar chart
// new Chart(document.getElementById("Chart1"), {
//     type: 'horizontalBar',
//     data: {
//         labels: [""],
//         datasets: [{
//             data: [positive_ratio],
//             backgroundColor: "rgba(63,203,226,1)",
//             hoverBackgroundColor: " rgba(46,185,235,1)"
//         }, {
//             data: [negative_ratio],
//             backgroundColor: "rgba(163,103,126,1)",
//             hoverBackgroundColor: "rgba(140,85,100,1)"
//         }, {
//             data: [neutral_ratio],
//             backgroundColor: "rgba(63,103,126,1)",
//             hoverBackgroundColor: "rgba(50,90,100,1)"
//         }]
//     },
//     options: barOptions_stacked,
//
// });


//line chart
new Chart(document.getElementById("line-chart"), {
    type: 'line',
    data: {
        labels: dateArray,
        datasets: [{
            label: '긍정',
            data: posArray,
            borderColor: "rgba(46, 255, 53, 0.8)",
            backgroundColor: "rgba(46, 255, 53, 0.1)",
            fill: false,
            lineTension: 0
        },{
            label: '부정',
            data: negArray,
            borderColor: "rgba(246, 26, 26, 0.8)",
            backgroundColor: "rgba(246, 26, 26, 0.1)",
            fill: false,
            lineTension: 0
        },{
            label: '중립',
            data: neuArray,
            borderColor: "rgba(48, 48, 48, 0.8)",
            backgroundColor: "rgba(48, 48, 48, 0.1)",
            fill: false,
            lineTension: 0
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: '라인 차트'
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'x축'
                }
            }],
            yAxes: [{
                display: true,
                ticks: {
                    suggestedMin: 0,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'y축'
                }
            }]
        }
    }
});

// $(function () {
//     const neg_array = []
//
//     for (let sentiment of sentimentArray){
//         neg_array.push(sentiment.document.confidence.negative)
//
//     }
// })


$(function() {
    const sum = sentimentArray.reduce((a,b)=>(a+b));

    // sentimentArray[0]: 부정, [1]: 중립, [2]: 긍정
    const neg_ratio = sentimentArray[0]/sum
    const neu_ratio = sentimentArray[1]/sum
    const pos_ratio = sentimentArray[2]/sum

    console.log(pos_ratio)
    console.log(neg_ratio)

    if (neg_ratio>0.333){
        $(document.body).toggleClass('negative')
        $('#sentiment').text('\'부정\'')
    }else if(pos_ratio>0.333){
        $(document.body).toggleClass('positive')
        $('#sentiment').text('\'긍정\'')

    }else{
        $(document.body).toggleClass('neutral')
        $('#sentiment').text('\'중립\'')

    }
    // $("div").css("position", "relative")

    })
