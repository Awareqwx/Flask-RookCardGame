$(document).ready(function(){
    followCards();
    text = "";
    $("#played .card").each(function(i){
        text += "<input type='hidden' name='card' value='" + i + "'>"
    });
    $("#cardlist").html(text)
    $("#hand .follow").hover(function(){
        $(this).css("border-color", "lightblue");
    }, function(){
        $(this).css("border-color", "black");
    });
    $("#hand .follow").click(function(){
        let cardNum = $(this).attr('id');
        console.log(cardNum, cardNum.substr(4));
        $("#selectedCard").html("<input type='hidden' name='cardPlayed' value='" + cardNum.substr(4) + "'>");
        console.log($('#trickform').serialize())
        $.ajax({
            url: '/game/trick',
            data: $('#trickform').serialize(),
            type: 'POST',
            success: function(res){
                console.log(res["url"]);
                location.href=res["url"];
            }
        });
    });
});

function followCards()
{
    if($("#played .card").length == 0)
    {
        $("#hand .card").each(function(){
            $(this).addClass("follow")
        })
    }
    else
    {
        let hasRook = false;
        $("#hand .card").each(function(i){
            if($(this).hasClass($("#follow").val()) || $(this).hasClass("cardRook"))
            {
                $(this).addClass("follow")
                console.log("Hello")
                if($(this).hasClass("cardRook"))
                {
                    hasRook = true;
                }
            }
            else
            {
                $(this).css("border-color", "red")
                console.log("World")
            }
        });
        if($(".follow").length === 0 && !hasRook)
        {
            console.log("Foo")
            $("#hand .card").each(function(){
                $(this).addClass("follow")
                $(this).css("border-color", "black")
            })
        }
        else if($(".follow").length == 1 && hasRook)
        {
            console.log("Bar")
            $("#hand .card").each(function(){
                $(this).addClass("follow")
                $(this).css("border-color", "black")
            })
        }
    }
}