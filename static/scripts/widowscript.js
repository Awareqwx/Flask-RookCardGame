var selected = 0;
var cards = [];

$(document).ready(function(){
    $(".card").hover(function(){
        if(!$(this).data("selected"))
        {
            $(this).css("border-color", "lightblue");
        }
    }, function(){
        if(!$(this).data("selected"))
        {
            $(this).css("border-color", "black");
        }
    });
    $(".card").click(function(){
        if($(this).data("selected"))
        {
            $(this).data("selected", false);
            $(this).css("border-color", "lightblue");
        }
        else
        {
            $(this).data("selected", true);
            $(this).css("border-color", "blue");
        }
        selected = 0;
        cards = [];
        $(".card").each(function(i){
            if($(this).data("selected"))
            {
                selected += 1
                cards[cards.length] = i
            }
        })
        console.log(cards)
        console.log(" ")
        if(selected == 5)
        {
            $("#widowform").show();
        }
        else
        {
            $("#widowform").hide();
        }
        var text = ""
        for(i in cards)
        {
            text += "<input type='hidden' name='card" + i + "' value='" + cards[i] + "'>"
        }
        $("#cardlist").html(text);
    });
    $("#widowform").hide();
});