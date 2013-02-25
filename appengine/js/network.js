$(function() {

  console.log("yeah");

  var topics = {
    "chordoma": 'chordoma.txt'
    , "ocular melanoma": 'ocular+melanoma.txt'
    , "polycythemia vera": 'polycythemia+vera.txt'
    , "skin melanoma": 'skin+melanoma.txt'
  }

  // grab the topics for typeahead provision
  var topic_keys = [];
  for (var k in topics) topic_keys.push(k);


  // prepopulate topic input
  $('#research-topic').val('chordoma');

  // setup typeahead for topic input
  $('#research-topic').typeahead({
    source: topic_keys
  });

  // wait for input to change
  $('#research-topic').change(function() {
    // get topic input
    var selection = $('#research-topic').val();

    if (selection in topics) {
      // load json
      load_graph(selection);
    }
  }).change();

  $('#clear-box').click(function(){
    $('#more-info-box').css('display', 'none');
  });

  // event handlers

  var offhover = function(d) {
    link.attr('stroke', '#999');
    node
      .attr('opacity', function(d){
        return 1;
      });
  };

  var hover = function(d) {
    var index = [];
    links.forEach(function(link,i){
      if ((link.source.x == d.x & link.source.y == d.y) | (link.target.x == d.x & link.target.y == d.y)){
        index.push(i);
      }
    });

    var num = Math.random()*40;

    d3.select("#hover-info")
      .html('Author' + 'Professor X' + "<br/>Papers: " + d.x);

    link.attr('stroke', function(d, i){
      if (index.indexOf(i) > -1) {
        return 'green';
      }
    });
  };

  var more_info = function(d) {
    $('#more-info-box').css('display', 'block');
    $('#more-info-box').css('left', mouseX);
    $('#more-info-box').css('top', mouseY);

    var index = 0;

    nodes.forEach(function(node,i){
      if (node.x == d.x & node.y == d.y){
        index = i;
      }
    });

    d3.select('#more-info-box')
      .html('Author ' + hold_authors[index].name + "<br/>Papers: " + hold_authors[index].paperCount);

    d3.select("#hover-info")
      .html('Author ' +  hold_authors[index].name + "<br/>Papers: " + hold_authors[index].paperCount + "<br/>PubMed papers:<br><ul></ul>"
    );

    $.map(hold_authors[index].papers, function(d){
      $('#hover-info ul').append('<li>'+d+'</li>');
    });
  };

  function processData(response) {
    console.log("Process data called");

    // data's loaded, clear out any old graphics
    $('.contain-graphic').html('');

    // build a new graphic
    var w = $('.contain-graphic').width(),
    h = $(window).height()-50,
    fill = d3.scale.category10(),
    nodes = d3.range(response.authorsOnly.length).map(Object),
    links = d3.range(response.authorPairs.length).map(Object);

    var hold_authors = d3.range(response.authorsOnly.length).map(Object);

    var index = 0;
    var mouseX = 0,
    mouseY = 0;

    for (var j = 0; j < response.authorPairs.length; j++){
      links[j] = {source: nodes[response.authorPairs[j].authorA], target: nodes[response.authorPairs[j].authorB], value: response.authorPairs[j].paperCount};
    }

    $.each(response.authorsOnly, function(i,entry){
      hold_authors[i] = {id: entry.name, name: entry.name, paperCount: entry.publicationIds.length, papers: entry.publicationIds };
    });

    var vis = d3.select(".contain-graphic").append("svg:svg")
      .attr("width", w)
      .attr("height", h);

    var force = d3.layout.force()
      .nodes(nodes)
      .links(links)
      .size([w, h])
      .start()
      .gravity('0.25')
      .charge(-40)
      .linkDistance(function(d){
        return 1000-d.value;
      });

    var link = vis.selectAll('.link')
      .data(links)
      .enter().append('line')
      .attr('class','link')
      .style('stroke-width',function(d){
        return Math.sqrt(d.value);
      })
      .attr('stroke','#999')
      .attr('stroke-opacity', '0.6')

    var node = vis.selectAll("circle.node")
      .data(nodes)
      .enter().append("svg:circle")
      .attr("class", "node")
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("r", function(d,i){
        return hold_authors[i].paperCount;
      })
      .attr('opacity', .6)
      .style("fill", function(d, i) { return 'red'; })
      .style("stroke", function(d, i) { return d3.rgb(fill(i & 3)).darker(2); })
      .style("stroke-width", 1.5)
      .on('click', more_info)

    vis.style("opacity", 1e-6)
      .transition()
      .duration(1000)
      .style("opacity", 1);

    force.on("tick", function(e) {
      // Push different nodes in different directions for clustering.
      var k = 6 * e.alpha;

      link.attr("x1", function(d) { return (d.source.x); })
        .attr("y1", function(d) { return (d.source.y); })
        .attr("x2", function(d) { return (d.target.x); })
        .attr("y2", function(d) { return (d.target.y); });

      node.attr("cx", function(d) { return (d.x); })
          .attr("cy", function(d) { return (d.y); });
    });
  }

  function load_graph(dataset) {
    // dataset is, for instance, "chordoma.txt"
    var url = "/disease/" + dataset + "/d3";
    $.getJSON(url, processData);
  }

});