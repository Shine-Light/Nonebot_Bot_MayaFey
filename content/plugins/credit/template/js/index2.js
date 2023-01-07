var money;
var count;
var sender_avatar;
var sender_nickname;
var datas;

class Data {
    constructor(data) {
        this.avatar = data['avatar'];
        this.money_get = data['record'][1];
        this.time = data['record'][2];
        this.nickname = data['record'][3];
        this.achievement = data['achievement'];
    }
}

function init() {
    var img_avatar_center = document.querySelector(".avatar-center img");
    var div_title = document.querySelector(".title");
    var div_money = document.querySelector(".money");
    var div_count = document.querySelector(".count");
    var container = document.querySelector(".container");

    img_avatar_center.src = "data:image/jpeg;base64," + sender_avatar;
    div_title.innerHTML = sender_nickname + div_title.innerHTML;
    div_money.innerHTML = money;
    div_count.innerHTML = count + div_count.innerHTML;

    for (let index = 0; index < datas.length; index++) {
        var li = document.createElement('li');
        var li_img = document.createElement('img');
        var li_span1 = document.createElement('span');
        var li_span2 = document.createElement('span');
        var li_span1_div_nickname = document.createElement('div');
        var li_span1_div_time = document.createElement('div');
        var li_span2_div_money_get = document.createElement('div');
        var li_span2_div_achievement = document.createElement('div');

        container.appendChild(li);
        li.appendChild(li_img);
        li.appendChild(li_span1);
        li_span1.appendChild(li_span1_div_nickname);
        li_span1.appendChild(li_span1_div_time);
        li.appendChild(li_span2);
        li_span2.appendChild(li_span2_div_money_get);
        li_span2.appendChild(li_span2_div_achievement);

        li_img.classList.add("avatar");
        li_img.src = "data:image/jpeg;base64," + datas[index].avatar;
        
        li_span1.classList.add("text1");
        li_span1_div_nickname.innerHTML = datas[index].nickname;
        li_span1_div_nickname.classList.add("nickname");
        li_span1_div_time.innerHTML = datas[index].time;
        li_span1_div_time.classList.add("time");

        li_span2.classList.add("text2");
        li_span2_div_money_get.innerHTML = datas[index].money_get + " 积分";
        li_span2_div_money_get.classList.add("money_get");
        li_span2_div_achievement.innerHTML = datas[index].achievement;
        li_span2_div_achievement.classList.add("achievement");
    }
}