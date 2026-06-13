package dataAll._app.setting
{
   import com.sounto.net.SWFLoaderUrl;
   import com.sounto.oldUtils.ComMethod;
   import com.sounto.utils.ClassProperty;
   import com.sounto.utils.TextMethod;
   import dataAll._app.setting.key.SettingKeySaveGroup;
   import dataAll.ui.GatherColor;
   import flash.media.SoundMixer;
   import flash.media.SoundTransform;
   import gameAll.image.ShootMouseCursor;
   
   public class SettingSave
   {
      
      public static var textArr:Array = ["allText","critText","spurtingText","hurtText"];
      
      public static var sceneArr:Array = ["pauseAffterOutB","autoLotteryB","firstChooseB","closeWhippB","bossLifeB","simpleNumberB"];
      
      public static var pro_arr:Array = [];
      
      public var sensitivity:Number = 0.3;
      
      public var shootShake:Number = 1;
      
      public var screenShake:Number = 0.6;
      
      public var ghostTeB:Boolean = false;
      
      public var pauseAffterOutB:Boolean = true;
      
      public var autoLotteryB:Boolean = false;
      
      public var firstChooseB:Boolean = false;
      
      public var closeWhippB:Boolean = false;
      
      public var bossLifeB:Boolean = false;
      
      public var simpleNumberB:Boolean = false;
      
      public var skillSpecialB:Boolean = false;
      
      public var trueBossB:Boolean = false;
      
      public var quality:String = "medium";
      
      public var blood:Number = 1;
      
      public var allText:Boolean = false;
      
      public var critText:Boolean = false;
      
      public var spurtingText:Boolean = false;
      
      public var hurtText:Boolean = false;
      
      public var filterEF:Boolean = false;
      
      public var noFloor:Boolean = true;
      
      public var frame:int = 120;
      
      public var cursor:String = "";
      
      public var volume:Number = 0.5;
      
      private var soundTransform:SoundTransform = new SoundTransform();
      
      public var loginMu:String = "";
      
      public var mainMu:String = "lost";
      
      public var partsSaB:Boolean = false;
      
      public var fontLeadB:Boolean = false;
      
      public var equip_batchSellColorArr:Array = ["white","green","blue"];
      
      public var equip_batchDecomposeColorArr:Array = ["white","green","blue"];
      
      public var gene_batchSellColorArr:Array = ["white","green","blue"];
      
      public var gene_batchDecomposeColorArr:Array = ["white","green","blue"];
      
      public var arms_batchSellColorArr:Array = ["white","green","blue"];
      
      public var arms_batchDecomposeColorArr:Array = ["white","green","blue"];
      
      public var echelonB:Boolean = false;
      
      public var key:SettingKeySaveGroup = new SettingKeySaveGroup();
      
      public var ver:int = 0;
      
      public function SettingSave()
      {
         super();
      }
      
      public static function setLocalLoginMusic(label0:String) : void
      {
         Gaming.api.save.localSave.setPro("loginMusic",label0);
      }
      
      public static function getLocalLoginMusic() : String
      {
         var arr0:Array = null;
         var v0:* = Gaming.api.save.localSave.getPro("loginMusic");
         var label0:String = "";
         if(v0 != null)
         {
            label0 = String(v0);
         }
         if(label0 == "")
         {
            arr0 = Gaming.defineGroup.staticCtrl.musicNameArr;
            label0 = arr0[0];
         }
         return label0;
      }
      
      public function initSave() : void
      {
         this.key.initObj();
      }
      
      public function inData_byObj(obj0:Object) : void
      {
         ClassProperty.inData_bySaveObj(this,obj0,pro_arr);
         if(this.quality == "")
         {
            this.quality = "medium";
         }
         if(!obj0.hasOwnProperty("key"))
         {
            this.key.initObj();
         }
         if(!obj0.hasOwnProperty("ver"))
         {
            if(this.screenShake > 0.6)
            {
               this.screenShake = 0.6;
            }
         }
         if(ShootMouseCursor.shootArr.indexOf(this.cursor) == -1)
         {
            this.cursor = ShootMouseCursor.shoot1;
         }
         setLocalLoginMusic(this.loginMu);
      }
      
      public function getValue(pro0:String) : *
      {
         if(this.hasOwnProperty(pro0))
         {
            return this[pro0];
         }
         return null;
      }
      
      public function haveValue(pro0:String) : Boolean
      {
         return this.hasOwnProperty(pro0);
      }
      
      public function setValue(pro0:String, v0:*) : void
      {
         this[pro0] = v0;
         if(pro0 == "volume")
         {
            this.soundTransform.volume = this.volume;
            SoundMixer.soundTransform = this.soundTransform;
         }
      }
      
      public function getFrame() : int
      {
         var f0:int = this.frame;
         if(f0 <= 0)
         {
            f0 = 120;
         }
         return f0;
      }
      
      public function setFrame30() : void
      {
         this.frame = 120;
      }

      public function setFrame(f0:int) : void
      {
         this.frame = f0;
      }
      
      public function getCursor() : String
      {
         if(this.cursor == "")
         {
            return ShootMouseCursor.shoot1;
         }
         return this.cursor;
      }
      
      public function fleshVolume() : void
      {
         this.setValue("volume",this.volume);
      }
      
      public function setQuality(str0:String) : void
      {
         this.quality = str0;
         if(str0 == "low")
         {
            this.blood = 0;
            this.allText = true;
            this.filterEF = true;
            this.noFloor = true;
         }
         else if(str0 == "medium")
         {
            this.blood = 0.5;
            this.allText = false;
            this.critText = false;
            this.spurtingText = true;
            this.hurtText = false;
            this.noFloor = true;
         }
         else if(str0 == "high")
         {
            this.blood = 1;
            this.allText = false;
            this.critText = false;
            this.spurtingText = false;
            this.hurtText = false;
         }
      }
      
      public function setEchelon() : void
      {
         this.echelonB = !this.echelonB;
      }
      
      public function getColorArr(type0:String, decomposeB0:Boolean) : Array
      {
         var ctrl0:String = decomposeB0 ? "Decompose" : "Sell";
         var name0:String = type0 + "_batch" + ctrl0 + "ColorArr";
         if(this.hasOwnProperty(name0))
         {
            return this[name0];
         }
         return [];
      }
      
      public function setColorArr(type0:String, decomposeB0:Boolean, arr0:Array) : void
      {
         var ctrl0:String = decomposeB0 ? "Decompose" : "Sell";
         var name0:String = type0 + "_batch" + ctrl0 + "ColorArr";
         if(this.hasOwnProperty(name0))
         {
            this[name0] = arr0;
         }
      }
      
      public function getLoginMusic() : String
      {
         return this.getMusic("login");
      }
      
      public function getMainMusic() : String
      {
         return this.getMusic("main");
      }
      
      private function getMuiscSwf(label0:String) : SWFLoaderUrl
      {
         var name0:String = this.getMusic(label0);
         return Gaming.defineGroup.staticCtrl.getMusic(name0);
      }
      
      private function getMusic(label0:String) : String
      {
         var arr0:Array = null;
         var music0:String = this[label0 + "Mu"];
         if(music0 == "")
         {
            arr0 = Gaming.defineGroup.staticCtrl.musicNameArr;
            music0 = arr0[0];
            this.setMusic(label0,music0);
         }
         return music0;
      }
      
      private function setMusic(label0:String, name0:String) : void
      {
         this[label0 + "Mu"] = name0;
         setLocalLoginMusic(this.loginMu);
      }
      
      public function swapMusic(label0:String) : void
      {
         var music0:String = this.getMusic(label0);
         var arr0:Array = Gaming.defineGroup.staticCtrl.musicNameArr;
         var f0:int = int(arr0.indexOf(music0));
         if(f0 == -1)
         {
            f0 = 0;
         }
         else
         {
            f0 = (f0 + 1) % arr0.length;
         }
         music0 = arr0[f0];
         this.setMusic(label0,music0);
      }
      
      public function getMusicText() : String
      {
         var s0:String = this.getMusicTextOne("login","登录音乐");
         return s0 + ("\n" + this.getMusicTextOne("main","主页音乐"));
      }
      
      private function getMusicTextOne(label0:String, title0:String) : String
      {
         var url0:SWFLoaderUrl = this.getMuiscSwf(label0);
         var s0:String = ComMethod.color(title0 + "：",GatherColor.gray2Color) + url0.cn + "  ";
         return s0 + TextMethod.link("切换",label0);
      }
   }
}

