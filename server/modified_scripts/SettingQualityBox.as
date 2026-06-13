package UI.setting
{
   import UI.NormalUICtrl;
   import UI.UIOrder;
   import UI.base.btnList.BtnBox;
   import UI.base.button.NormalBtn;
   import UI.base.event.ClickEvent;
   import UI.base.label.LabelBox;
   import UI.base.scroll.SliderBar;
   import dataAll._app.setting.SettingSave;
   import flash.display.Sprite;
   import flash.events.MouseEvent;
   import gameAll.image.ShootMouseCursor;
   
   public class SettingQualityBox extends BtnBox
   {
      
      public var bloodBar:SliderBar = new SliderBar();
      
      private var bloodSp:Sprite;
      
      private var cursorTag:Sprite;
      
      private var cursorBox:LabelBox = new LabelBox();
      
      public function SettingQualityBox()
      {
         super();
      }
      
      override public function setImg(img0:Sprite) : void
      {
         elementNameArr = ["bloodSp","cursorTag"];
         super.setImg(img0);
         addChild(this.cursorBox);
         NormalUICtrl.setTag(this.cursorBox,this.cursorTag);
         this.cursorBox.arg.init(99,1,5,0);
         this.cursorBox.addEventListener(ClickEvent.ON_CLICK,this.cursorClick);
         addChild(this.bloodBar);
         this.bloodBar.setImg(this.bloodSp);
         this.bloodBar.setChangeFun(this.barChange);
         this.bloodBar.label = "blood";
      }
      
      override protected function SET(str0:String, value0:Object) : void
      {
         if(!this[str0])
         {
            this[str0] = value0;
         }
      }
      
      override public function show() : void
      {
         var grip0:NormalBtn = null;
         if(this.cursorBox.gripArr.length == 0)
         {
            this.cursorBox.inData("BasicUI/cursorBtn",ShootMouseCursor.shootArr,ShootMouseCursor.shootArr);
            for each(grip0 in this.cursorBox.gripArr)
            {
               grip0.setIconName(ShootMouseCursor.getBmpUrl(grip0.label));
            }
         }
         super.show();
         this.fleshData();
      }
      
      private function get settingSave() : SettingSave
      {
         return Gaming.PG.save.setting;
      }
      
      public function fleshData() : void
      {
         var btn0:NormalBtn = null;
         var label0:String = null;
         var bb0:Boolean = false;
         if(!Gaming.PG.save)
         {
            return;
         }
         this.bloodBar.setPer(this.settingSave.getValue("blood"));
         var textArr0:Array = SettingSave.textArr;
         for each(btn0 in btnArr)
         {
            label0 = btn0.label;
            if(this.settingSave.haveValue(label0))
            {
               bb0 = this.settingSave.getValue(label0);
               btn0.activedAndIgnoreChosen = true;
               btn0.isChosen = bb0;
            }
            if(textArr0.indexOf(label0) >= 0)
            {
               if(label0 != "allText")
               {
                  btn0.actived = !this.settingSave.getValue("allText");
               }
            }
         }
         this.fleshFrameBtn();
         this.cursorBox.setChoose(this.settingSave.getCursor());
         Gaming.EG.fleshSetting();
         Gaming.BGHit.fleshSetting();
         Gaming.uiGroup.fleshSetting();
         UIOrder.fleshSettingReadSave();
         this.fleshStat();
      }
      
      private function fleshFrameBtn() : void
      {
         var btn0:NormalBtn = null;
         var actived0:Boolean = !Gaming.uiGroup.stopHandUpBox.getStopAccB();
         btn0 = getBtn("frame");
         btn0.actived = actived0;
         btn0.setName("游戏帧频：" + this.settingSave.getFrame());
      }
      
      private function fleshStat() : void
      {
         var btn0:NormalBtn = getBtn("stat");
         btn0.isChosen = Gaming.uiGroup.getStatVisible();
      }
      
      override protected function btnClick(e:MouseEvent) : void
      {
         var bb0:Boolean = false;
         if(!Gaming.PG.save)
         {
            return;
         }
         var btn0:NormalBtn = e.target as NormalBtn;
         var label0:String = btn0.label;
         if(label0 == "stat")
         {
            Gaming.uiGroup.showStat(!Gaming.uiGroup.getStatVisible());
            this.fleshStat();
         }
         else if(label0 == "frame")
         {
            Gaming.uiGroup.alertBox.showNumChoose("设定游戏帧频3~120",this.settingSave.getFrame(),120,3,1,this.afterFrame);
         }
         else if(this.settingSave.haveValue(label0))
         {
            bb0 = this.settingSave.getValue(label0);
            this.settingSave.setValue(label0,!bb0);
            this.fleshData();
         }
      }
      
      private function afterFrame(v0:int) : void
      {
         this.settingSave.setFrame(v0);
         this.fleshFrameBtn();
         UIOrder.fleshSettingReadSave();
      }
      
      private function barChange(v0:Number, label0:String) : void
      {
         if(Boolean(Gaming.PG.save))
         {
            this.settingSave.setValue(label0,v0);
         }
      }
      
      private function cursorClick(e:ClickEvent) : void
      {
         if(Boolean(Gaming.PG.save))
         {
            this.cursorBox.setChoose(e.label);
            this.settingSave.cursor = e.label;
            UIOrder.fleshSettingReadSave();
         }
      }
      
      public function FTimerSecond() : void
      {
         if(visible)
         {
         }
      }
   }
}

