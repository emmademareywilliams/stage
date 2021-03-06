<?php
/*
    All Emoncms code is released under the GNU General Public License v3.
    See COPYRIGHT.txt and LICENSE.txt.
    ---------------------------------------------------------------------
    Emoncms - open source energy visualisation
    Part of the OpenEnergyMonitor project: http://openenergymonitor.org
*/
    global $path, $embed;

    $type = 1;
?>

<!--[if IE]><script language="javascript" type="text/javascript" src="<?php echo $path;?>Lib/flot/excanvas.min.js"></script><![endif]-->
<script language="javascript" type="text/javascript" src="<?php echo $path; ?>Lib/flot/jquery.flot.merged.js"></script>

<script language="javascript" type="text/javascript" src="<?php echo $path; ?>Modules/vis/visualisations/common/api.js"></script>
<script language="javascript" type="text/javascript" src="<?php echo $path; ?>Modules/vis/visualisations/common/inst.js"></script>
<script language="javascript" type="text/javascript" src="<?php echo $path; ?>Modules/vis/visualisations/common/proc.js"></script>


<?php if (!$embed) { ?>
<h2><?php echo _("Datapoint editor:"); ?> <?php echo $feedidname; ?></h2>
<p><?php echo _("Click on a datapoint to select, then in the edit box below the graph enter in the new value. You can also add another datapoint by changing the time to a point in time that does not yet have a datapoint."); ?></p>
<?php } ?>

<div id="graph_bound" style="height:350px; width:100%; position:relative;">

<!-- copié : création d'un nouvel objet, qui sera le graphe de référence : -->
    <div id="reference"></div>
    <div id="graph-buttons" style="position:absolute; top:18px; right:32px; opacity:0.5;">
        <div class='btn-group'>
            <button class='btn graph-time' type='button' time='1'>D</button>
            <button class='btn graph-time' type='button' time='7'>W</button>
            <button class='btn graph-time' type='button' time='30'>M</button>
            <button class='btn graph-time' type='button' time='365'>Y</button>
        </div>

        <div class='btn-group' id='graph-navbar' style='display: none;'>
            <button class='btn graph-nav' id='zoomin'>+</button>
            <button class='btn graph-nav' id='zoomout'>-</button>
            <button class='btn graph-nav' id='left'><</button>
            <button class='btn graph-nav' id='right'>></button>
        </div>
    </div>
    <div id="graph"></div>
    <h3 style="position:absolute; top:0px; left:32px;"><span id="stats"></span></h3>
</div>

<div style="width:100%; height:50px; background-color:#ddd; padding:10px; margin:10px;">
    <?php echo _("Edit feed_"); ?><?php echo $feedid; ?> <?php echo _("@ time:"); ?> <input type="text" id="time" style="width:150px;" value="" /> <?php echo _("new value:"); ?>
    <input type="text" id="newvalue" style="width:150px;" value="" />
    <button id="okb" class="btn btn-info"><?php echo _('Save'); ?></button>
    <button id="delete-button" class="btn btn-danger"><i class="icon-trash"></i><?php echo _('Delete data in window'); ?></button>
</div>

<div style="width:100%; height:50px; background-color:#ddd; padding:10px; margin:10px;">
    <?php echo _("Multiply data in the window by a float or a fraction"); ?> <input type="text" id="multiplyvalue" style="width:150px;" value="" />
    <button id="multiply-submit" class="btn btn-info"><?php echo _('Save'); ?></button>
    <?php echo _("<br>To erase all the window with NAN > type NAN - To convert all the window to absolute values > type abs(x)"); ?>
</div>

<div id="myModal" class="modal hide" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" data-backdrop="static">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
        <h3 id="myModalLabel"><?php echo _('Delete feed data'); ?></h3>
    </div>
    <div class="modal-body">
        <p><?php echo _('Deleting feed data in this window is permanent.'); ?>
           <br><br>
           <?php echo _('Are you sure you want to delete?'); ?>
        </p>
    </div>
    <div class="modal-footer">
        <button class="btn" data-dismiss="modal" aria-hidden="true"><?php echo _('Cancel'); ?></button>
        <button id="confirmdelete" class="btn btn-primary"><?php echo _('Delete permanently'); ?></button>
    </div>
</div>

<script id="source" language="javascript" type="text/javascript">
  $('#graph').width($('#graph_bound').width());
  $('#graph').height($('#graph_bound').height()/2);

// copié : pour fixer la hauteur et la largeur du nouveau graphe :
// (on divise la hauteur (qui est fixée) par 2 pour que les 2 graphes rentrent bien)
  $('#reference').width($('#graph_bound').width());
  $('#reference').height($('#graph_bound').height()/2);

  var feedid = "<?php echo $feedid; ?>";
  var ref = "<?php echo $ref; ?>";
  var temp = "<?php echo $temp; ?>";
  var feedname = "<?php echo $feedidname; ?>";
  var type = "<?php echo $type; ?>";
  var apikey = "<?php echo $write_apikey; ?>";

  var timeWindow = (3600000*24.0*7);        //Initial time window
  var start = ((new Date()).getTime())-timeWindow;    //Get start time
  var end = (new Date()).getTime();       //Get end time

  var feed_interval = false;

  vis_feed_data();

  function vis_feed_data()
  {

    $.ajax({
      url: path+'feed/getmeta.json',
      data: "&apikey="+apikey+"&id="+feedid,
      dataType: 'json',
      async: false,
      success: function(result) {
          if (result && result.interval!=undefined) {
              feed_interval = result.interval;
          }
      }
    });

    function plot_pump(feednb)
    /*
    plots the pump operation graph in the bottom graph
    feednb: number of the feed that we want to plot --> will be the pump feed nb
    */
    {
        var graph_data = get_feed_data(feednb,start,end,interval,1,0);
        var stats = power_stats(graph_data);
        // if line graph:
        var plotdata = {label: "pompe", data: graph_data, lines: { show: true, fill: true }};
        // if bar graph:
        if (type == 2) plotdata = {data: graph_data, yaxis: yaxisnb, bars: { show: true, align: "center", barWidth: 3600*18*1000, fill: true}};
        var plot = $.plot($("#graph"), [plotdata], {
          canvas: true,
          grid: { show: true, hoverable: true, clickable: true },
          xaxis: { mode: "time", timezone: "browser", min: start, max: end },
          legend: { show: true, noColumns: 0, position: "se", backgroundColor: "white", lineWidth: 0},
          selection: { mode: "x" },
          touch: { pan: "x", scale: "x" }
        });

        $("#graph").bind("plotclick", function (event, pos, item) {
          if (item != null) {
            $("#time").val(item.datapoint[0]/1000);
            $("#newvalue").val(item.datapoint[1]);
          }
        });
      }

      function plot_reference(feed1, feed2)
      /*
      plots the references in the top graph
      feed1: first reference feed (will be North circuit departure temperature)
      feed2: second reference feed (will be North indoor temperature)
      */
      {
          var graph_data1 = get_feed_data(feed1,start,end,interval,1,0);
          var graph_data2 = get_feed_data(feed2,start,end,interval,1,0);
          //var stats = power_stats(graph_data);
          // if line graph:
          var plotdata = [
            {label: "circuit temp", data: graph_data1, yaxis: 1, color: "pink", lines: { show: true, fill: true }},
            {label: "indoor temp", data: graph_data2, yaxis: 2, color: "yellow", lines: { show: true, fill: false }}
          ];
          // if bar graph:
          if (type == 2) {
            plotdata = [
              {label: "label1", data: graph_data1, yaxis: 1, bars: { show: true, align: "center", barWidth: 3600*18*1000, fill: true}},
              {label: "label2", data: graph_data2, yaxis: 2, bars: { show: true, align: "center", barWidth: 3600*18*1000, fill: true}}
            ];
          }
          var plot = $.plot($("#reference"), plotdata, {
            canvas: true,
            grid: { show: true, hoverable: true, clickable: true },
            xaxis: { mode: "time", timezone: "browser", min: start, max: end },
            yaxes: [ { position: "left" }, { position: "right" } ],
            legend: { show: true, noColumns: 1, position: "se", backgroundColor: "white", lineWidth: 0},
            selection: { mode: "x" },
            touch: { pan: "x", scale: "x" }
          });

          $("#reference").bind("plotclick", function (event, pos, item) {
            if (item != null) {
              $("#time").val(item.datapoint[0]/1000);
              $("#newvalue").val(item.datapoint[1]);
            }
          });
        }

    var npoints = 800;
    interval = Math.round(((end - start)/npoints)/1000);

    var outinterval = 5;
    if (interval>10) outinterval = 10;
    if (interval>15) outinterval = 15;
    if (interval>20) outinterval = 20;
    if (interval>30) outinterval = 30;
    if (interval>60) outinterval = 60;
    if (interval>120) outinterval = 120;
    if (interval>180) outinterval = 180;
    if (interval>300) outinterval = 300;
    if (interval>600) outinterval = 600;
    if (interval>900) outinterval = 900;
    if (interval>1200) outinterval = 1200;
    if (interval>1800) outinterval = 1800;
    if (interval>3600*1) outinterval = 3600*1;
    if (interval>3600*2) outinterval = 3600*2;
    if (interval>3600*3) outinterval = 3600*3;
    if (interval>3600*4) outinterval = 3600*4;
    if (interval>3600*5) outinterval = 3600*5;
    if (interval>3600*6) outinterval = 3600*6;
    if (interval>3600*12) outinterval = 3600*12;
    if (interval>3600*24) outinterval = 3600*24;

    interval = outinterval;
    if (feed_interval && interval<feed_interval) interval = feed_interval;

    start = Math.floor((start*0.001) / interval) * interval * 1000;
    end = Math.ceil((end*0.001) / interval) * interval * 1000;

    plot_pump(feedid);
    plot_reference(ref, temp);

  }


 function zoom_toolbox(str_graph)
 /*
 str_graph: name of the graph (string) associated with the feed number, defined at the beginning
 */
 {
   $(str_graph).bind("plotselected", function (event, ranges) { start = ranges.xaxis.from; end = ranges.xaxis.to; vis_feed_data(); });

   // the buttons appear when the mouse pointer passes over the graph:
   $(str_graph).mouseenter(function(){
     $("#graph-navbar").show();
     $("#graph-buttons").stop().fadeIn();
     $("#stats").stop().fadeIn();
   });
 // the buttons disappear when the mouse is out of the frame:
   $(str_graph).bind("touchstarted", function (event, pos)
   {
     $("#graph-navbar").hide();
     $("#graph-buttons").stop().fadeOut();
     $("#stats").stop().fadeOut();
   });

  // action:
   $(str_graph).bind("touchended", function (event, ranges)
   {
     $("#graph-buttons").stop().fadeIn();
     $("#stats").stop().fadeIn();
     start = ranges.xaxis.from; end = ranges.xaxis.to;
     vis_feed_data();
   });
 }

  //--------------------------------------------------------------------------------------
  // Graph zooming toolbox
  //--------------------------------------------------------------------------------------

  //----------------------------------------------------------------------------------------------
  // Operate buttons --> do not change, whatever the graph
  //----------------------------------------------------------------------------------------------
  $("#zoomout").click(function () {inst_zoomout(); vis_feed_data();});
  $("#zoomin").click(function () {inst_zoomin(); vis_feed_data();});
  $('#right').click(function () {inst_panright(); vis_feed_data();});
  $('#left').click(function () {inst_panleft(); vis_feed_data();});
  $('.graph-time').click(function () {inst_timewindow($(this).attr("time")); vis_feed_data();});
  //-----------------------------------------------------------------------------------------------

  $('#okb').click(function () {
    var time = $("#time").val();
    var newvalue = $("#newvalue").val();

    console.log(time+" "+newvalue);

    $.ajax({
      url: path+'feed/update.json',
      data: "&apikey="+apikey+"&id="+feedid+"&time="+time+"&value="+newvalue+"&skipbuffer=1",
      dataType: 'json',
      async: false,
      success: function() {}
    });
    vis_feed_data();
  });

  $('#multiply-submit').click(function () {

    var multiplyvalue = $("#multiplyvalue").val();
    console.log(multiplyvalue);

    $.ajax({
      url: path+'feed/scalerange.json',
      data: "&apikey="+apikey+"&id="+feedid+"&start="+start+"&end="+end+"&value="+multiplyvalue,
      dataType: 'json',
      async: false,
      success: function(result) {
          alert(result)
      }
    });
    vis_feed_data();
  });

  $('#delete-button').click(function () {
    $('#myModal').modal('show');
  });

  $("#confirmdelete").click(function()
  {
    $.ajax({
      url: path+'feed/deletedatarange.json',
      data: "&apikey="+apikey+"&id="+feedid+"&start="+start+"&end="+end,
      dataType: 'json',
      async: false,
      success: function(result) {
          alert(result)
      }
    });
    vis_feed_data();
    $('#myModal').modal('hide');
  });

// Call to the zoom_toolbox function:
 zoom_toolbox("#reference");
 zoom_toolbox("#graph");

 $("#graph_bound").mouseleave(function(){
   $("#graph-buttons").stop().fadeOut();
   $("#stats").stop().fadeOut();
 });


</script>
