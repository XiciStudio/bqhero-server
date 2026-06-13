package
{
   import UI.UIGroup;
   import UI.UIShow;
   import UI.api.AllAPI;
   import UI.base.font.FontDeal;
   import UI.base.tip.TextGatherAnalyze;
   import UI.loading.LoadingUI;
   import UI.pay.PayCtrl;
   import com.sounto.image.BmpEffectDataManager;
   import com.sounto.key.KeysGroup;
   import com.sounto.net.SWFLoaderManager;
   import com.sounto.net.TextLoaderManager;
   import com.sounto.oldUtils.Copyright;
   import com.sounto.oldUtils.Sounto64;
   import com.sounto.sound.SoundGroup;
   import dataAll._base.LocalXmlLoader;
   import dataAll._data.ConstantDefine;
   import dataAll._data.DefineGroup;
   import dataAll._player.PlayerCtrl;
   import dataAll._player.PlayerCtrlGrop;
   import dataAll._player.PlayerData;
   import dataAll._player.count.props.DpsCountCtrl;
   import dataAll._player.role.RoleName;
   import dataAll.arms.creator.GunImageManager;
   import dataAll.image.ImageUrlDefine;
   import dataAll.image.ImageUrlFather;
   import dataAll.test.DefineBugTest;
   import flash.display.MovieClip;
   import flash.display.Sprite;
   import flash.display.StageQuality;
   import flash.display.StageScaleMode;
   import flash.events.Event;
   import flash.events.KeyboardEvent;
   import flash.events.MouseEvent;
   import flash.geom.Rectangle;
   import flash.system.Security;
   import flash.system.System;
   import flash.utils.getTimer;
   import gameAll.bodyGroup.BodyGroup;
   import gameAll.bodyGroup.hit.BodyGroupHit;
   import gameAll.bullet.BulletGroup;
   import gameAll.drop.body.DropBodyGroup;
   import gameAll.effect.EffectGroup;
   import gameAll.image.GameSprite;
   import gameAll.image.ShootMouseCursor;
   import gameAll.level.LevelGroup;
   import gameAll.process.PretreatmentGroup;
   import gameAll.say.SayBoxGroup;
   import gameAll.scene.SceneGroup;
   import gameAll.scene.TargetInputController;
   import gameAll.trigger.TriggerGroup;
   import w_test.AllTestCtrl;

   [SWF(frameRate="144",backgroundColor="#000000",width="950",height="600")]
   public class Gaming extends MovieClip
   {

      public static var ME:Gaming;

      public static var serviceHold:* = null;

      private static var sounto64:int = Sounto64.random();

      private static var textGatherAnalyze:int = TextGatherAnalyze.init();

      private static var fontGap:int = FontDeal.init();

      public static const WIDTH:int = 950;

      public static const HEIGHT:int = 600;

      public static const APP_UI_HEIGHT:int = 530;

      public static const GAMING_RANGE:Rectangle = new Rectangle(10,65,784,475);

      public static var swfLoaderManager:SWFLoaderManager = new SWFLoaderManager();

      public static var textLoaderManager:TextLoaderManager = new TextLoaderManager();

      public static var soundGroup:SoundGroup = new SoundGroup();

      public static var defineGroup:DefineGroup = new DefineGroup();

      public static var gunImageManager:GunImageManager = new GunImageManager();

      public static var keyGroup:KeysGroup = new KeysGroup();

      public static var EG:EffectGroup = new EffectGroup();

      public static var sayBox:SayBoxGroup = new SayBoxGroup();

      public static var gameSprite:GameSprite = new GameSprite();

      public static var BG:BodyGroup = new BodyGroup();

      public static var bulletGroup:BulletGroup = new BulletGroup();

      public static var dropGroup:DropBodyGroup = new DropBodyGroup();

      public static var BGHit:BodyGroupHit = new BodyGroupHit();

      public static var sceneGroup:SceneGroup = new SceneGroup();

      public static var targetInput:TargetInputController = new TargetInputController();

      public static var TG:TriggerGroup = new TriggerGroup();

      public static var LG:LevelGroup = new LevelGroup();

      public static var pretreatGroup:PretreatmentGroup = new PretreatmentGroup();

      public static var PG:PlayerCtrl = new PlayerCtrl();

      public static var PCG:PlayerCtrlGrop = new PlayerCtrlGrop();

      public static var uiGroup:UIGroup = new UIGroup();

      public static var api:AllAPI = new AllAPI();

      public static var testCtrl:AllTestCtrl = new AllTestCtrl();

      private static var secondLoadB:Boolean = true;

      private static var secondLoadYesFun:Function = null;

      private static var secondLoadVar:Object = null;

      private var noticeUIClass:Class = Gaming_noticeUIClass;

      public var noticeUIMc:Sprite = new this.noticeUIClass();

      private var _4399_function_store_id:String = "3885799f65acec467d97b4923caebaae";

      private var _4399_function_rankList_id:String = "69f52ab6eb1061853a761ee8c26324ae";

      private var _4399_function_shop_id:String = "30ea6b51a23275df624b781c3eb43ac6";

      private var _4399_function_payMoney_id:String = "10f73c09b41d9f41e761232f5f322f38";

      private var _4399_function_union_id:String = "7c7a741b186b91e2975006321918345f";

      private var loadingUI:LoadingUI = new LoadingUI();

      private var copyright:Copyright;

      private var xmlLoader:LocalXmlLoader = new LocalXmlLoader();

      // ---- Delta-time accumulator for high-FPS rendering with fixed-step logic ----
      private var _lastTime:Number = 0;
      private var _accumulator:Number = 0;
      private static const LOGIC_HZ:int = 30;
      private static const LOGIC_DT:Number = 1000.0 / LOGIC_HZ;

      public function Gaming()
      {
         super();
         Security.allowDomain("*");
         System.useCodePage = false;
         ME = this;
         if(Boolean(stage))
         {
            this.xmlLoad();
         }
         else
         {
            addEventListener(Event.ADDED_TO_STAGE,this.xmlLoad);
         }
      }

      public static function secondLoad(yesFun0:Function, var0:Object) : void
      {
         secondLoadYesFun = yesFun0;
         secondLoadVar = var0;
         if(secondLoadB)
         {
            yesSecondLoad();
            return;
         }
         swfLoaderManager.addEventListener(Event.COMPLETE,yesSecondLoad);
         secondLoadB = true;
         uiGroup.loadingUI.show();
         swfLoaderManager.startLoad();
      }

      private static function yesSecondLoad(e:Event = null) : void
      {
         swfLoaderManager.removeEventListener(Event.COMPLETE,yesSecondLoad);
         var fun0:Function = secondLoadYesFun;
         secondLoadYesFun = null;
         fun0(secondLoadVar);
         secondLoadVar = null;
      }

      public static function fouseToStage() : void
      {
         ME.stage.focus = ME.stage;
      }

      public static function getSaveIndex() : int
      {
         return PG.getSaveIndex();
      }

      public static function getUid() : String
      {
         return PG.getUid();
      }

      public static function isLocal() : Boolean
      {
         return api.save.isLocal();
      }

      public static function isLoginAndHaveUid() : Boolean
      {
         if(api.save.isLogin())
         {
            if(Boolean(PG.loginData))
            {
               if(isLocal())
               {
                  return true;
               }
               if(PG.loginData.uidZeroB() == false)
               {
                  return true;
               }
            }
         }
         return false;
      }

      public function setHold(hold:*) : void
      {
         serviceHold = hold;
      }

      private function xmlLoad(e:Event = null) : void
      {
         if(Boolean(e))
         {
            removeEventListener(Event.ADDED_TO_STAGE,this.xmlLoad);
         }
         PayCtrl.staticInit();
         this.xmlLoader.init(this.yes_xmlLoad,this);
      }

      private function yes_xmlLoad(out0:Object) : void
      {
         defineGroup.setXmlOut(out0);
         this.firstLoad();
      }

      private function firstLoad(e:Event = null) : void
      {
         addChild(gameSprite);
         this.mouseEnabled = false;
         stage.scaleMode = StageScaleMode.NO_SCALE;
         stage.showDefaultContextMenu = false;
         stage.stageFocusRect = false;
         uiGroup.loadingUI = this.loadingUI;
         this.loadingUI.setCon(gameSprite.cover);
         this.loadingUI.loadResouce(this.textLoad);
      }

      private function textLoad() : void
      {
         this.textLoader_complete2();
      }

      private function textLoader_complete2(e:Event = null) : void
      {
         ConstantDefine.staticInit();
         defineGroup.propertyAdd();
         PG.propertyAdd();
         defineGroup.init();
         PG.init();
         var dd:* = defineGroup;
         if(isLocal() || this.loaderInfo.loaderURL.indexOf(ConstantDefine.testUrl) >= 0)
         {
            swfLoaderManager.addSWFLoader("swf/UI/TestUI.swf","TestUI","UI");
            stage.scaleMode = StageScaleMode.SHOW_ALL;
         }
         else
         {
            INIT.errorB = false;
         }
         swfLoaderManager.addSWFLoader("swf/UI/TestUI.swf","TestUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/YuanXiaoUI295.swf","YuanXiaoUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/TowerUI323.swf","TowerUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/SpaceUI302.swf","SpaceUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/BosseditUI317.swf","BosseditUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/OtherUI319.swf","OtherUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/AnniverUI314.swf","AnniverUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/DemonUI274.swf","DemonUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/FoodUI.swf","FoodUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/WilderUI317.swf","WilderUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/BasicUI322.swf","BasicUI","UI");
         swfLoaderManager.addSWFLoader("swf/UI/IconGather321.swf","IconGather","图标");
         swfLoaderManager.addSWFLoader("swf/UI/SkillIcon324.swf","SkillIcon","图标");
         swfLoaderManager.addSWFLoader("swf/UI/AchieveIcon318.swf","AchieveIcon","图标");
         swfLoaderManager.addSWFLoader("swf/UI/ThingsIcon324.swf","ThingsIcon","图标");
         swfLoaderManager.addSWFLoader("swf/UI/PartsIcon324.swf","PartsIcon","图标");
         swfLoaderManager.addSWFLoader("swf/UI/BodyImg324.swf","BodyImg","图标");
         swfLoaderManager.addSWFLoader("swf/UI/MainUI320.swf","MainUI","UI");
         swfLoaderManager.addSWFLoader("swf/equip/equipGather315.swf","equipGather","装备");
         swfLoaderManager.addSWFLoader("swf/equip/equipIcon203.swf","equipIcon","装备图标");
         swfLoaderManager.addSWFLoader("swf/UI/uiGather324.swf","uiGather","UI");
         swfLoaderManager.addSWFLoader("swf/gun/gunGather322.swf","gunGather","武器");
         swfLoaderManager.addSWFLoader("swf/effect/effectGather322.swf","effectGather","特效");
         swfLoaderManager.addSWFLoader("swf/hero/Striker309.swf","Striker","人物");
         swfLoaderManager.addSWFLoader("swf/hero/Girl316.swf","Girl","雇佣兵");
         swfLoaderManager.addSWFLoader("swf/hero/XinLing.swf","XinLing","雇佣兵");
         swfLoaderManager.addSWFLoader("swf/hero/XiaoMei.swf","XiaoMei","雇佣兵");
         swfLoaderManager.addSWFLoader("swf/enemy/RifleHornetShooter.swf","RifleHornetShooter","其他");
         swfLoaderManager.addSWFLoader("swf/enemy/Bat.swf","Bat","其他");
         swfLoaderManager.addSWFLoader("swf/effect/generalEffect323.swf","generalEffect","特效");
         swfLoaderManager.addSWFLoader("swf/effect/skillEffect315.swf","skillEffect","特效");
         swfLoaderManager.addSWFLoader("swf/effect/boomEffect322.swf","boomEffect","特效");
         swfLoaderManager.addSWFLoader("swf/effect/bulletHitEffect307.swf","bulletHitEffect","特效");
         swfLoaderManager.addSWFLoader("swf/effect/smokeEffect.swf","smokeEffect","特效");
         swfLoaderManager.addSWFLoader("swf/music/music_face298.swf","music_face","音乐");
         swfLoaderManager.addSWFLoader("swf/music/music_main210.swf","music_main","音乐");
         swfLoaderManager.addSWFLoader("swf/sound/sound294.swf","sound","音效");
         swfLoaderManager.addSWFLoader("swf/sound/uiSound285.swf","uiSound","音效");
         swfLoaderManager.addSWFLoader("swf/sound/boomSound298.swf","boomSound","音效");
         swfLoaderManager.addSWFLoader("swf/sound/hitSound309.swf","hitSound","音效");
         swfLoaderManager.addSWFLoader("swf/sound/bodySound.swf","bodySound","音效");
         swfLoaderManager.addSWFLoader("swf/hero/WenJie.swf","WenJie","雇佣兵");
         swfLoaderManager.addSWFLoader("swf/hero/ZangShi.swf","ZangShi","雇佣兵");
         swfLoaderManager.addSWFLoader("swf/hero/XiaoMeiZombie.swf","XiaoMeiZombie","雇佣兵");
         swfLoaderManager.addSWFLoader("swf/gun/specialGun324.swf","specialGun","武器");
         swfLoaderManager.addSWFLoader("swf/weapon/weapon324.swf","weapon","兵器");
         swfLoaderManager.addEventListener(Event.COMPLETE,this.swfLoader_complete);
         swfLoaderManager.startLoad();
      }

      private function swfLoader_complete(e:Event) : void
      {
         swfLoaderManager.removeEventListener(Event.COMPLETE,this.swfLoader_complete);
         this.game_init();
      }

      public function game_init() : void
      {
         var all_t0:Number = getTimer();
         var eg0:EffectGroup = EG;
         pretreatGroup.processBody(RoleName.Striker);
         pretreatGroup.processBody(RoleName.Girl);
         pretreatGroup.processBody("RifleHornetShooter");
         EG.bmpMovieM.addBodyResourceKeep("RifleHornetShooter");
         pretreatGroup.processBody("Bat");
         EG.bmpMovieM.addBodyResourceKeep("Bat");
         defineGroup.body.dealMovieLink();
         api.init();
         gunImageManager.swfM = swfLoaderManager;
         sayBox.init();
         soundGroup.init(swfLoaderManager);
         sceneGroup.init();
         targetInput.init();
         BG.init();
         bulletGroup.init();
         BGHit.init();
         EG.init();
         LG.init();
         uiGroup.init();
         testCtrl.afterUIInit(this.loaderInfo.loaderURL);
         var dd:* = defineGroup;
         soundGroup.addSound_bySwfInside("sound",["metal_hit1","metal_hit2","main_vehicle","sub_vehicle","noCharger","swapStart","swapEnd","launchStart","launchEnd","launchStart1","launchEnd1"]);
         soundGroup.addSound_bySwfInside("uiSound",["swapHero","getLottery","moveLottery","mapChange","changeLabel","winTime","failTime","levelup","giveupTask","getTask","fail","swapSuccess","alertShow","sell","buy","errorClick","click","skillNoTarget","showPointer","sayShow","mobile","sayHide","getItems","success"]);
         this.effect_init();
         stage.quality = StageQuality.MEDIUM;
         gameSprite.addEventListener(MouseEvent.CLICK,testCtrl.mouseClickFun);
         gameSprite.L_mouse.addEventListener(MouseEvent.MOUSE_DOWN,this.mouseDown);
         gameSprite.L_mouse.addEventListener(MouseEvent.MOUSE_UP,this.mouseUp);
         stage.addEventListener(Event.MOUSE_LEAVE,this.mouseLeave);
         stage.addEventListener(Event.DEACTIVATE,this.focusLeave);
         stage.addEventListener(Event.ENTER_FRAME,this.FTimer);
         stage.addEventListener(KeyboardEvent.KEY_UP,this.keyUp);
         stage.addEventListener(KeyboardEvent.KEY_DOWN,this.keyDown);
         uiGroup.hideAllAppUI();
         uiGroup.hideAllBackUI();
         UIShow.login();
         if(testCtrl.enabled)
         {
            DefineBugTest.check();
         }
      }

      private function effect_init() : void
      {
         var imgD0:ImageUrlDefine = null;
         var tt0:Number = getTimer();
         EG.bmpMovieM.addResource(swfLoaderManager.getResource("skillEffect","aircraft"),"skillEffect","aircraft");
         EG.bmpEffectM.addResourceListKeep(["skillEffect/superEnemy","skillEffect/trueBoss","skillEffect/groupLight_hero"]);
         EG.bmpEffectM.addResourceListKeep(["bulletHitEffect/yellow_motion","bulletHitEffect/smoke_small","bulletHitEffect/spark_motion"],25);
         EG.bmpEffectM.addResourceListKeep(["gunFire/f1","gunFire/f2"],30);
         EG.bmpEffectM.addResourceListKeep(["skillEffect/energyShield"],1);
         EG.bmpEffectM.addResourceListKeep(["lightEffect/darkgoldDrop","lightEffect/blackDrop","lightEffect/blueDrop","lightEffect/whiteDrop","lightEffect/greenDrop","lightEffect/purpleDrop","lightEffect/redDrop","lightEffect/orangeDrop","lightEffect/basinShow","lightEffect/purgoldDrop"]);
         EG.bmpEffectM.addResourceListKeep(["boomEffect/boom1","boomEffect/boom2","boomEffect/boom3","boomEffect/showLight"],1);
         EG.bmpEffectM.addResourceListKeep([BmpEffectDataManager.zeroEFUrl],1);
         EG.bmpEffectM.addResourceListKeep(["bladeHitEffect/blood"],15);
         EG.bmpEffectM.addResourceListKeep(["textEffect/t1"],1);
         EG.bmpEffectM.addResourceListKeep(["bullet/gaiaSmallBullet"],30);
         EG.bmpEffectM.addResourceListKeep(["generalEffect/equipLight1","generalEffect/equipLight2","generalEffect/equipLight3","generalEffect/overKey","generalEffect/fKey","generalEffect/weaponKill"],1);
         EG.bmpEffectM.addResourceListKeep(["Striker/swordAttackLeft","Striker/swordAttackRight"],1);
         EG.bmpEffectM.addResourceListKeep(ShootMouseCursor.getBmpUrlArr(),1);
         EG.bmpEffectM.addResourceListKeep(["GameWorldUI/noCharger"],1);
         EG.textEffectG.addResoure(".-+0123456789 万亿%");
         EG.textEffectG.addResoure("弹药丢失秒杀","GREEN");
         EG.textEffectG.addResoure("反弹暴击背包已满","RED");
         EG.textEffectG.addResoure("获得物品武器装备血量弹药基因体置副手食材","YELLOW");
         EG.textEffectG.addResoure("闪避丢失","PURPLE");
         ShootMouseCursor.register();
         var defineArr0:Array = defineGroup.imageUrl.getArrByFather(ImageUrlFather.bulletLine);
         for each(imgD0 in defineArr0)
         {
            if(imgD0.isLongLine() == false)
            {
               EG.bmpEffectM.addImgUrlDefineKeep(imgD0);
            }
         }
         EG.bmpEffectM.addImgUrlDefineName("boomMove");
         EG.bmpEffectM.addImgUrlDefineName("boomMoveSmall");
         EG.bmpEffectM.addImgUrlDefineName("stoneMoveSmall");
         EG.bmpEffectM.addImgUrlDefineName("greenBlood");
         EG.bmpEffectM.addImgUrlDefineName("whiteBlood");
         EG.bmpEffectM.addImgUrlDefineName("spark");
         EG.bmpEffectM.addImgUrlDefineName("fire");
         EG.bmpEffectM.addImgUrlDefineName("stone");
         EG.bmpEffectM.addImgUrlDefineName("zombieDie");
      }

      private function mouseDown(e:MouseEvent) : void
      {
         targetInput.mouseDown(e);
      }

      private function mouseUp(e:MouseEvent = null) : void
      {
         targetInput.mouseUp(e);
      }

      private function keyDown(e:KeyboardEvent) : void
      {
         testCtrl.keyDown(e);
         targetInput.keyDown(e);
         uiGroup.keyDown(e);
         if(LG.state == "ing")
         {
            LG.keyDown(e);
            keyGroup.keyDown(e);
         }
      }

      private function keyUp(e:KeyboardEvent) : void
      {
         targetInput.keyUp(e);
         uiGroup.keyUp(e);
         if(LG.state == "ing")
         {
            keyGroup.keyUp(e);
         }
      }

      private function mouseLeave(e:Event) : void
      {
      }

      private function focusLeave(e:Event) : void
      {
         targetInput.focusLeave(e);
         uiGroup.focusLeave(e);
      }

      private function FTimer(e:* = null) : void
      {
         var now:Number = getTimer();
         if (_lastTime == 0)
         {
            _lastTime = now;
         }
         var delta:Number = now - _lastTime;
         _lastTime = now;

         // Prevent spiral of death after tab switch / pause
         if (delta > 200)
         {
            delta = 200;
         }

         _accumulator += delta;

         // Run game logic at fixed 30Hz step
         while (_accumulator >= LOGIC_DT)
         {
            _accumulator -= LOGIC_DT;

            if (LG.state == "ing")
            {
               BG.startTimer();
               targetInput.FTimer();
               soundGroup.inSceneMidde(sceneGroup.getMiddleX(), sceneGroup.getMiddleY());
               sceneGroup.senceTimer();
               EG.bmpEffectM.dataTimer(gameSprite.L_game.x, gameSprite.L_game.y);
               bulletGroup.FTimer();
               dropGroup.FTimer();
               BG.FTimer();
               BG.imageTimer();
               BGHit.FTimer();
               LG.FTimer();
               sayBox.FTimer();
               keyGroup.KeyTimer();
               gameSprite.FTimer();
               EG.imageTimer();
               DpsCountCtrl.FTimer();
            }
         }

         // Cap accumulator to prevent huge catch-up after long pause
         if (_accumulator > LOGIC_DT * 5)
         {
            _accumulator = LOGIC_DT * 5;
         }

         // UI updates run every frame at full FPS
         DpsCountCtrl.allFTimer();
         testCtrl.FTimer();
         pretreatGroup.FTimer();
         if (PG.da is PlayerData)
         {
            PG.FTimer(LG);
            uiGroup.FTimer();
         }
         uiGroup.FTimerAll();
      }
   }
}
