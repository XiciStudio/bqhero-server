package gameAll.body.motion
{
   import com.sounto.hit.anyShape.AnyShapeRect;
   import com.sounto.math.Maths;
   import com.sounto.motion.CoorMotion;
   import com.sounto.motion.DofHitType;
   import com.sounto.motion.Motion_DOFData;
   import com.sounto.utils.NumberMethod;
   import dataAll._player.role.RoleName;
   import dataAll.body.define.BodyEditDefine;
   import dataAll.body.define.BodyFlyType;
   import dataAll.body.define.HeroDefine;
   import dataAll.body.define.NormalBodyDefine;
   import flash.geom.Rectangle;
   import flash.utils.getDefinitionByName;
   import gameAll.body.IO_NormalBody;
   
   public class NormalGroundMotion extends CoorMotion
   {
      
      private static var aircraftClass:AircraftGroundMotion;
      
      public static const _FG:Number = 60 * 30 / (INIT.FPS * INIT.FPS);
      
      public static var FGMul:Number = 1;
      
      public static var FFMul:Number = 1;
      
      public var _def:NormalBodyDefine = null;
      
      public var motionEnabled:Boolean = true;
      
      public var bodyDieB:Boolean = false;
      
      public var state:String = "stand";
      
      public var STAND_HIT_RECT:Rectangle = new Rectangle(-12,-90,24,90);
      
      public var SQUAT_HIT_RECT:Rectangle = new Rectangle(-12,-50,24,50);
      
      public var HIT_RECT:Rectangle = this.STAND_HIT_RECT;
      
      public var hitRect:AnyShapeRect = new AnyShapeRect();
      
      public var MX:int = 0;
      
      public var MY:int = 0;
      
      public var before_vy:Number = 0;
      
      public var slope_vy:Number = 0;
      
      public var Fi_vxmax:Number = 5;
      
      public var Fi_vymax:Number = 33.333333333333336;
      
      public var Fi_vx:Number = 0;
      
      public var Fi_vy:Number = 0;
      
      public var e_vx:Number = 0;
      
      public var e_vy:Number = 0;
      
      public var state_e_vx:Number = 0;
      
      public var state_e_vy:Number = 0;
      
      public var dof:Motion_DOFData = new Motion_DOFData();
      
      public var inRangeLimitB:Boolean = false;
      
      public var noRangeLimitB:Boolean = false;
      
      public var playerRangeLimitB:Boolean = false;
      
      public var MOVE_MAX:Number = 5;
      
      public var RUN_MAX:Number = 11.666666666666666;
      
      public var noSpeedReduceB:Boolean = false;
      
      private var maxStateValue:Number = 0;
      
      public var maxStateMul:Number = 1;
      
      public var dropSpeedMul:Number = 1;
      
      public var allMaxStateMul:Number = 1;
      
      public var out_maxStateMul:Number = 1;
      
      public var outOfWorldB:Boolean = false;
      
      private var jumpMustVxMax:Number = 0;
      
      public var F_G:Number = 2;
      
      public var F_Gstate:Number = 1;
      
      public var F_I:Number = 6.666666666666667;
      
      public var F_F:Number = this.F_I / 2;
      
      public var F_Fstate:Number = 1;
      
      public var F_A:Number = this.F_I / 15;
      
      public var fi:Number = 0;
      
      public var ff:Number = 0;
      
      public var fg:Number = 0;
      
      public var JUMP_H:Number = 170;
      
      public var JUMP_VY:Number = Math.sqrt(2 * this.JUMP_H * this.F_G);
      
      public var nowJumpNum:int = 0;
      
      public var nowSprintNum:int = 0;
      
      public var maxJumpNum:int = 1;
      
      public var maxJumpNumAdd:int = 0;
      
      private var jumpTarget_mx:int = -100000;
      
      private var jumpTarget_my:int = -100000;
      
      private var delayFun:Function;
      
      public var delayT:int = -100;
      
      public var isSlopeVyB:Boolean = false;
      
      public var ra:Number = 0;
      
      public var vra:Number = 0;
      
      public var ara:Number = 0;
      
      public var raBySlopeB:Boolean = false;
      
      public var F_I_AIR:Number = 2;
      
      private var tween_x:Number = 100;
      
      private var tween_y:Number = 100;
      
      private var stopFly_xB:Boolean = false;
      
      private var stopFly_yB:Boolean = false;
      
      public var flyType:String = "normal";
      
      public var countFlyB:Boolean = false;
      
      private var nowIsAirB:Boolean = false;
      
      private var nowFallFirstY:int = -10000;
      
      public var maxFallHigh:int = 0;
      
      public var maxFlyHigh:int = 0;
      
      public function NormalGroundMotion()
      {
         super();
      }
      
      public static function staticStartLevel() : void
      {
         FGMul = 1;
         FFMul = 1;
      }
      
      public static function getMotionClass(name0:String) : NormalGroundMotion
      {
         var class0:Class = null;
         var b0:NormalGroundMotion = null;
         if(name0 == "")
         {
            return new NormalGroundMotion();
         }
         class0 = getDefinitionByName("gameAll.body.motion." + name0) as Class;
         return new class0();
      }
      
      public function isLandState() : Boolean
      {
         return this.state == GroundMotionState.stand;
      }
      
      public function toLand() : void
      {
         this.state = GroundMotionState.stand;
      }
      
      public function isFlyState() : Boolean
      {
         return this.state == GroundMotionState.fly;
      }
      
      public function initState() : void
      {
         this.maxStateMul = 1;
         this.allMaxStateMul = 1;
         this.maxStateValue = 0;
         this.dropSpeedMul = 1;
         this.state_e_vx = 0;
         this.state_e_vy = 0;
         this.outOfWorldB = false;
         this.F_Fstate = 1;
         this.F_Gstate = 1;
      }
      
      public function addSpeedState(mul0:Number = 1, v0:Number = 0, maxMul0:Number = 999, noReduceEffectB0:Boolean = false) : void
      {
         if(this.noSpeedReduceB && !noReduceEffectB0)
         {
            if(mul0 < 1)
            {
               mul0 = 1;
            }
            if(v0 < 0)
            {
               v0 = 0;
            }
         }
         this.maxStateMul *= mul0;
         this.maxStateValue += v0;
         if(this.maxStateMul > maxMul0)
         {
            this.maxStateMul = maxMul0;
         }
      }
      
      public function setMaxState(mul0:Number, v0:Number) : void
      {
         this.maxStateMul *= mul0;
         this.maxStateValue += v0;
      }
      
      public function addDropSpeedState(mul0:Number, vyMax0:Number = -1) : void
      {
         this.dropSpeedMul *= mul0;
         if(vyMax0 >= 0)
         {
            if(this.Fi_vy > vyMax0)
            {
               this.Fi_vy = vyMax0;
            }
         }
      }
      
      public function limitVx(v0:int) : void
      {
         if(v0 == -1)
         {
            if(this.Fi_vx < 0)
            {
               this.Fi_vx = 0;
            }
            if(vx < 0)
            {
               vx = 0;
            }
         }
         else if(v0 == 1)
         {
            if(this.Fi_vx > 0)
            {
               this.Fi_vx = 0;
            }
            if(vx > 0)
            {
               vx = 0;
            }
         }
      }
      
      override public function setX(value:Number) : void
      {
         x = value;
         mx = value;
      }
      
      override public function setY(value:Number) : void
      {
         y = value;
         my = value;
      }
      
      public function fleshByDefine(def:NormalBodyDefine) : void
      {
         this._def = def;
         this.HIT_RECT = def.hitRect;
         this.hitRect.inData(this.HIT_RECT);
         this.MOVE_MAX = def.maxVx;
         if(!def.extraDropArmsB && def.name != RoleName.MAIN)
         {
            this.MOVE_MAX *= 1 + (2 * Math.random() - 1) * def.motionD.vRan;
         }
         this.Fi_vxmax = this.MOVE_MAX;
         this.Fi_vymax = def.maxVy;
         this.F_G *= def.motionD.F_G;
         this.F_I *= def.motionD.F_I;
         this.F_F = this.F_I * def.motionD.F_F;
         if(def.motionD.F_AIR > 0)
         {
            this.F_I_AIR = def.motionD.F_AIR;
         }
         this.tween_x = def.motionD.tween;
         this.tween_y = this.tween_x;
         this.JUMP_H *= def.motionD.jumpMul;
         this.fleshJumpVy();
         this.state = def.motionState;
         this.flyType = def.flyType;
         this.raBySlopeB = def.rotateBySlopeB;
         this.maxJumpNum = def.maxJumpNum;
         var editD0:BodyEditDefine = def.getEditDNull();
         if(Boolean(editD0))
         {
            if(editD0.raIfNoMapB)
            {
               if(Gaming.LG.getNowWorldMapName() != def.map)
               {
                  this.raBySlopeB = true;
                  if(this.maxJumpNum == 0)
                  {
                     this.maxJumpNum = 2;
                  }
               }
            }
         }
      }
      
      public function fleshByHeroDefine(def:HeroDefine) : void
      {
         this.fleshByDefine(def);
         this.STAND_HIT_RECT = def.hitRect;
         this.SQUAT_HIT_RECT = def.squatHitRect;
         this.MOVE_MAX = def.squatMaxVx;
         this.RUN_MAX = def.maxVx;
         if(def.name != RoleName.MAIN)
         {
            this.RUN_MAX = def.maxVx * (0.85 + 0.3 * Math.random());
         }
      }
      
      public function fleshJumpVy() : void
      {
         this.JUMP_VY = Math.sqrt(2 * this.JUMP_H * this.F_G);
      }
      
      public function setFlyType(type0:String) : void
      {
         this.flyType = type0;
      }
      
      public function flyTo(mx0:Number, my0:Number) : void
      {
         mx = mx0;
         this.stopFly_xB = false;
         my = my0;
         this.stopFly_yB = false;
      }
      
      public function flyToBody(b0:IO_NormalBody) : void
      {
         if(Boolean(b0))
         {
            this.flyTo(b0.getMot().MX,b0.getMot().MY);
         }
      }
      
      public function toStop() : void
      {
         this.fi = 0;
         if(this.isSlopeVyB && this.Fi_vy < 0 && this.Fi_vy > -5)
         {
            this.Fi_vy = 0;
         }
         if(this.state == GroundMotionState.fly)
         {
            mx = x;
            my = y;
         }
      }
      
      public function moveToLeft() : void
      {
         if(this.dof.down == 1)
         {
            this.fi = -this.getFI();
         }
         else
         {
            this.fi = -this.getFI() / 3;
         }
      }
      
      public function moveToRight() : void
      {
         if(this.dof.down == 1)
         {
            this.fi = this.getFI();
         }
         else
         {
            this.fi = this.getFI() / 3;
         }
      }
      
      public function moveByMx(x0:Number, minGap0:int) : void
      {
         var gap0:Number = Math.abs(x0 - x);
         if(gap0 > minGap0)
         {
            if(x > x0)
            {
               this.moveToLeft();
            }
            else
            {
               this.moveToRight();
            }
         }
         else
         {
            this.toStop();
         }
      }
      
      public function getMoveDirection() : int
      {
         if(this.fi < 0)
         {
            return -1;
         }
         if(this.fi > 0)
         {
            return 1;
         }
         return 0;
      }
      
      public function toMaxMove(s0:int) : void
      {
         this.Fi_vx = this.Fi_vxmax * Maths.Pn(s0);
         if(!(s0 > 0 && this.dof.right == 1 || s0 < 0 && this.dof.left == 1))
         {
            x += s0;
            mx = x;
         }
      }
      
      public function setFi_vx_mul(v0:Number) : void
      {
         this.Fi_vx *= v0;
      }
      
      public function setFIMax(v0:Number) : void
      {
         this.MOVE_MAX = v0;
         this.Fi_vxmax = v0;
         this.Fi_vymax = v0;
      }
      
      public function setFiV_ra(v0:Number, ra0:Number) : void
      {
         if(this.isLandState())
         {
            this.Fi_vx = Math.cos(ra0) * v0;
         }
         else
         {
            this.setFiV_raAir(v0,ra0);
         }
      }
      
      public function setFiV_raAir(v0:Number, ra0:Number) : void
      {
         this.Fi_vx = Math.cos(ra0) * v0;
         this.Fi_vy = Math.sin(ra0) * v0;
      }
      
      public function toMove(x0:Number, y0:Number) : void
      {
         if(!((x0 > 0 && this.dof.right == 1 || x0 < 0 && this.dof.left == 1) && !this.outOfWorldB))
         {
            x += x0;
            mx = x;
         }
         if(!((y0 > 0 && this.dof.down == 1 || y0 < 0 && this.dof.up == 1) && !this.outOfWorldB))
         {
            y += y0;
            my = y;
         }
      }
      
      public function toMovePoint(x0:Number, y0:Number) : void
      {
         this.toMove(x0 - x,y0 - y);
      }
      
      public function getGap_slop() : Number
      {
         if(this.dof.slopeY <= -10000)
         {
            return 1000;
         }
         return this.dof.slopeY - (this.hitRect.y + this.hitRect.height);
      }
      
      public function isGroundB() : Boolean
      {
         return this.getGap_slop() <= 15 || this.dof.down == 1;
      }
      
      public function getBeFollowMx() : Number
      {
         return x;
      }
      
      public function getBeFollowMy() : Number
      {
         var gap0:Number = this.dof.slopeY;
         if(gap0 - y <= this.JUMP_H && gap0 < 10000)
         {
            return gap0;
         }
         return y;
      }
      
      public function getMaxJumpNum() : int
      {
         return this.maxJumpNum + this.maxJumpNumAdd;
      }
      
      public function toJump(highMul0:Number = 1, mx0:Number = -100000, my0:Number = -100000) : void
      {
         var cy1:int = 0;
         var cy2:int = 0;
         if(this.state == GroundMotionState.stand)
         {
            cy1 = this.hitRect.n3.y - this.hitRect.n3.maxY;
            cy2 = this.hitRect.n4.y - this.hitRect.n4.maxY;
            cy1 = cy1 > cy2 ? cy1 : cy2;
            if(cy1 > 0)
            {
               if(cy1 > 25 && (this.dof.left == 1 || this.dof.right == 1))
               {
                  cy1 = 5;
               }
               else if(cy1 > 20)
               {
                  cy1 = 20;
               }
               cy1 += 2;
            }
            if(cy1 < 5)
            {
               cy1 = 5;
            }
            if(highMul0 > 0)
            {
               y -= cy1 + 20;
            }
            this.dof.down = 0;
            if(this.nowJumpNum == 0)
            {
               this.Fi_vy = -this.JUMP_VY * highMul0;
            }
            else
            {
               this.Fi_vy = -this.JUMP_VY * 0.8 * highMul0;
            }
            if(this.maxStateMul == 0)
            {
               this.Fi_vy *= 0.02;
            }
            this.isSlopeVyB = false;
            ++this.nowJumpNum;
            if(mx0 == -100000)
            {
               mx0 = this.jumpTarget_mx;
               my0 = this.jumpTarget_my;
            }
            if(mx0 != -100000)
            {
               this.jumpMustVxMax = this.getJumpVx_byTarget(mx0,my0);
            }
            else
            {
               this.jumpMustVxMax = 0;
            }
         }
      }
      
      public function getJumpVx_byTarget(mx0:int, my0:int) : Number
      {
         var t2:Number = NaN;
         var t0:Number = NaN;
         var mvx0:Number = 0;
         var cx0:Number = mx0 - x;
         var cy0:Number = y - my0;
         var g0:Number = this.getFG();
         var t1:Number = this.JUMP_VY / g0;
         var h0:Number = 0.5 * g0 * t1 * t1;
         var ch0:Number = h0 - cy0;
         if(ch0 > 0 && cy0 > 0)
         {
            t2 = Math.sqrt(2 / g0);
            t0 = t1 + t2;
            mvx0 = cx0 / t0;
         }
         else
         {
            mvx0 = cx0 / (t1 * 2);
         }
         mvx0 = Math.abs(mvx0);
         if(mvx0 > this.Fi_vxmax * 2)
         {
            mvx0 = this.Fi_vxmax * 2;
         }
         else if(mvx0 < this.Fi_vxmax * 0.2)
         {
            mvx0 = 0;
         }
         return mvx0;
      }
      
      public function delayToJump(tt:Number, mx0:Number = -100000, my0:Number = -100000) : void
      {
         this.delayFun = this.toJump;
         this.delayT = tt * 30;
         this.jumpTarget_mx = mx0;
         this.jumpTarget_my = my0;
      }
      
      private function delayHandler() : void
      {
         if(this.delayT > 0)
         {
            this.delayT -= 1;
         }
         else if(this.delayT != -100)
         {
            this.delayFun();
            this.delayFun = null;
            this.delayT = -100;
         }
      }
      
      protected function raSlopeCount() : void
      {
         var mRa0:Number = this.dof.slopeAngle;
         if(Math.abs(mRa0) > Math.PI / 3.3)
         {
            mRa0 = 0;
         }
         this.inputSlopeRa(mRa0);
      }
      
      protected function inputSlopeRa(mRa0:Number, groundNoRoteB:Boolean = true) : void
      {
         this.ra = Maths.ZhunJ(this.ra);
         var pn0:int = this.ra - mRa0 > 0 ? -1 : 1;
         var cra0:Number = Maths.J_J(this.ra,mRa0);
         var vra0:Number = Math.abs(cra0) / 6;
         var mul0:Number = this.Fi_vxmax / 140;
         if(mul0 < 0.05)
         {
            mul0 = 0.05;
         }
         if(mul0 > 0.02)
         {
            mul0 = 0.02;
         }
         if(vra0 > Math.PI * mul0)
         {
            vra0 = Math.PI * mul0;
         }
         if(vra0 < 0.001)
         {
            vra0 = 0;
         }
         if(vx == 0 && vra0 < 0.005)
         {
            vra0 = 0;
         }
         if(groundNoRoteB)
         {
            if(!this.isGroundB())
            {
               vra0 = 0;
            }
         }
         this.vra = pn0 * vra0;
         this.ra += this.vra;
      }
      
      protected function inputRa(mRa0:Number) : void
      {
         this.ra = mRa0;
      }
      
      protected function flyCount() : void
      {
         if(this.flyType == BodyFlyType.normal)
         {
            this.normalFlyCount();
         }
         else if(this.flyType == BodyFlyType.tween)
         {
            this.tweenFlyCount();
         }
         else if(this.flyType == BodyFlyType.space)
         {
            this.spaceFlyCount();
         }
         if(this.dof.left == 1)
         {
            if(this.Fi_vx < 0)
            {
               this.Fi_vx = 0;
            }
            if(this.e_vx < 0)
            {
               this.e_vx = 0;
            }
            if(ax < 0)
            {
               ax = 0;
            }
            if(this.dof.left_back >= 2)
            {
               x += this.dof.left_back;
            }
         }
         if(this.dof.right == 1)
         {
            if(this.Fi_vx > 0)
            {
               this.Fi_vx = 0;
            }
            if(this.e_vx > 0)
            {
               this.e_vx = 0;
            }
            if(ax > 0)
            {
               ax = 0;
            }
            if(this.dof.right_back >= 2)
            {
               x -= this.dof.right_back;
            }
         }
         if(this.dof.up == 1)
         {
            if(this.Fi_vy < 0)
            {
               this.Fi_vy = 0;
            }
            if(this.e_vy < 0)
            {
               this.e_vy = 0;
            }
            if(ay < 0)
            {
               ay = 0;
            }
            if(this.dof.up_back >= 2)
            {
               y += this.dof.up_back;
            }
         }
         if(this.dof.down == 1)
         {
            if(this.Fi_vy > 0)
            {
               this.Fi_vy = 0;
            }
            if(this.e_vy > 0)
            {
               this.e_vy = 0;
            }
            if(ay > 0)
            {
               ay = 0;
            }
            if(this.dof.down_back >= 2)
            {
               y -= this.dof.down_back;
            }
         }
         vx = this.Fi_vx + this.e_vx + this.state_e_vx;
         vy = this.Fi_vy + this.e_vy + this.state_e_vy;
         if(vx > vxmax)
         {
            vx = vxmax;
         }
         else if(vx < -vxmax)
         {
            vx = -vxmax;
         }
         if(vy > vymax)
         {
            vy = vymax;
         }
         else if(vy < -vymax)
         {
            vy = -vymax;
         }
         x += vx * MainMotion.SPEED_SCALE;
         y += vy * MainMotion.SPEED_SCALE;
      }

      private function spaceFlyCount() : void
      {
         var ra0:Number = NaN;
         var mx0:Number = mx;
         var my0:Number = my;
         var cx0:Number = mx0 - x;
         var cy0:Number = my0 - y;
         var clen:Number = Math.sqrt(cx0 * cx0 + cy0 * cy0);
         var can0:Number = Math.atan2(cy0,cx0);
         var fi0:Number = this.F_I_AIR;
         var ff0:Number = this.F_I_AIR / 4;
         var vmax0:Number = (this.Fi_vxmax * this.maxStateMul * this.out_maxStateMul + this.maxStateValue) * this.allMaxStateMul;
         var v0:Number = Math.sqrt(this.Fi_vx * this.Fi_vx + this.Fi_vy * this.Fi_vy);
         var slowLen0:Number = 1;
         if(fi0 > 0)
         {
            slowLen0 = v0 * v0 / (2 * ff0) + 5;
         }
         if(clen <= slowLen0)
         {
            ra0 = Math.atan2(this.Fi_vy,this.Fi_vx);
            if(v0 <= ff0 * 2)
            {
               ax = 0;
               ay = 0;
               this.Fi_vx = 0;
               this.Fi_vy = 0;
            }
            else
            {
               ax = -ff0 * Math.cos(ra0);
               ay = -ff0 * Math.sin(ra0);
            }
         }
         else
         {
            ax = fi0 * Math.cos(can0);
            ay = fi0 * Math.sin(can0);
         }
         this.Fi_vx += ax;
         this.Fi_vy += ay;
         ra0 = Math.atan2(this.Fi_vy,this.Fi_vx);
         var xvmax0:Number = Math.abs(vmax0 * Math.cos(ra0));
         var yvmax0:Number = Math.abs(vmax0 * Math.sin(ra0));
         this.Fi_vx = NumberMethod.limitRange(this.Fi_vx,-xvmax0,xvmax0);
         this.Fi_vy = NumberMethod.limitRange(this.Fi_vy,-yvmax0,yvmax0);
      }
      
      private function normalFlyCount() : void
      {
         var fi_vmax0:Number = NaN;
         var tweenGap0:Number = NaN;
         var can0:Number = NaN;
         var vx_max0:Number = NaN;
         var vy_max0:Number = NaN;
         var va0:Number = NaN;
         var sx0:Number = NaN;
         var vax0:Number = NaN;
         var sy0:Number = NaN;
         var vay0:Number = NaN;
         var mx0:Number = mx;
         var my0:Number = my;
         var cx0:Number = mx0 - x;
         var cy0:Number = my0 - y;
         if(Math.abs(cx0) <= Math.abs(this.Fi_vx))
         {
            this.Fi_vx = 0;
            x = mx0;
            cx0 = 0;
         }
         if(Math.abs(cy0) <= Math.abs(this.Fi_vy))
         {
            this.Fi_vy = 0;
            y = my0;
            cy0 = 0;
         }
         var clen:Number = cx0 * cx0 + cy0 * cy0;
         if(clen > 1)
         {
            fi_vmax0 = (this.Fi_vxmax * this.maxStateMul * this.out_maxStateMul + this.maxStateValue) * this.allMaxStateMul;
            tweenGap0 = 30;
            can0 = Math.atan2(cy0,cx0);
            vx_max0 = Math.cos(can0) * fi_vmax0;
            vy_max0 = Math.sin(can0) * fi_vmax0;
            va0 = this.F_I_AIR;
            sx0 = Math.abs(this.Fi_vx * this.Fi_vx / 2 / va0);
            vax0 = Math.abs(cx0) < tweenGap0 ? Math.abs(cx0) / tweenGap0 * va0 : va0;
            if(cx0 * this.Fi_vx < 0)
            {
               sx0 = 0;
            }
            if(cx0 > sx0 || cx0 > -sx0 && cx0 < 0)
            {
               ax = vax0;
            }
            else
            {
               ax = -vax0;
            }
            this.Fi_vx += ax;
            if(vx_max0 > 0)
            {
               if(this.Fi_vx > vx_max0)
               {
                  this.Fi_vx = vx_max0;
               }
               else if(this.Fi_vx < -fi_vmax0)
               {
                  this.Fi_vx = -fi_vmax0;
               }
            }
            else if(vx_max0 < 0)
            {
               if(this.Fi_vx < vx_max0)
               {
                  this.Fi_vx = vx_max0;
               }
               else if(this.Fi_vx > fi_vmax0)
               {
                  this.Fi_vx = fi_vmax0;
               }
            }
            else
            {
               this.Fi_vx = 0;
            }
            sy0 = Math.abs(this.Fi_vy * this.Fi_vy / 2 / va0);
            vay0 = Math.abs(cy0) < tweenGap0 ? Math.abs(cy0) / tweenGap0 * va0 : va0;
            if(cy0 * this.Fi_vy < 0)
            {
               sy0 = 0;
            }
            if(cy0 > sy0 || cy0 > -sy0 && cy0 < 0)
            {
               ay = vay0;
            }
            else
            {
               ay = -vay0;
            }
            this.Fi_vy += ay;
            if(vy_max0 > 0)
            {
               if(this.Fi_vy > vy_max0)
               {
                  this.Fi_vy = vy_max0;
               }
               else if(this.Fi_vy < -fi_vmax0)
               {
                  this.Fi_vy = -fi_vmax0;
               }
            }
            else if(vy_max0 < 0)
            {
               if(this.Fi_vy < vy_max0)
               {
                  this.Fi_vy = vy_max0;
               }
               else if(this.Fi_vy > fi_vmax0)
               {
                  this.Fi_vy = fi_vmax0;
               }
            }
            else
            {
               this.Fi_vy = 0;
            }
         }
      }
      
      public function setPlayerCtrl(bb0:Boolean) : void
      {
      }
      
      public function setFlyTween(v0:int) : void
      {
         this.tween_x = v0;
         this.tween_y = this.tween_x;
      }
      
      protected function tweenFlyCount() : void
      {
         var cx:Number = mx - x;
         var cy:Number = my - y;
         var cx0:Number = Math.abs(cx);
         var cy0:Number = Math.abs(cy);
         var fi_vmax0:Number = (this.Fi_vxmax * this.maxStateMul * this.out_maxStateMul + this.maxStateValue) * this.allMaxStateMul;
         var fi_vmay0:Number = fi_vmax0;
         ax = this.F_I_AIR;
         if(cx0 < this.tween_x)
         {
            ax = cx0 / this.tween_x * this.F_I_AIR;
         }
         ax *= cx > 0 ? 1 : -1;
         this.Fi_vx += ax;
         if(this.Fi_vx > fi_vmax0)
         {
            this.Fi_vx = fi_vmax0;
         }
         else if(this.Fi_vx < -fi_vmax0)
         {
            this.Fi_vx = -fi_vmax0;
         }
         if(this.stopFly_xB && Math.abs(this.Fi_vx) <= 2)
         {
            this.Fi_vx = 0;
         }
         ay = this.F_I_AIR;
         if(cy0 < this.tween_y)
         {
            ay = cy0 / this.tween_y * this.F_I_AIR;
         }
         ay *= cy > 0 ? 1 : -1;
         this.Fi_vy += ay;
         if(this.Fi_vy > fi_vmay0)
         {
            this.Fi_vy = fi_vmay0;
         }
         else if(this.Fi_vy < -fi_vmay0)
         {
            this.Fi_vy = -fi_vmay0;
         }
         if(this.stopFly_yB && Math.abs(this.Fi_vy) <= 2)
         {
            this.Fi_vy = 0;
         }
      }
      
      protected function getFG() : Number
      {
         return this.F_G * FGMul * this.F_Gstate;
      }
      
      protected function getFF() : Number
      {
         return this.F_F * FFMul * this.F_Fstate;
      }
      
      protected function getFI() : Number
      {
         var v0:Number = FFMul;
         if(v0 < 0.2)
         {
            v0 = 0.2;
         }
         return this.F_I * v0;
      }
      
      protected function baseCount() : void
      {
         var e_ra:Number = NaN;
         var e_vy0:Number = NaN;
         var FG0:Number = this.getFG();
         this.before_vy = this.Fi_vy;
         this.slope_vy = 0;
         var FF0:Number = this.getFF();
         var ff0:Number = FF0;
         if(this.dof.down == 1)
         {
            this.fg = 0;
            ff0 = FF0;
         }
         else
         {
            this.fg = FG0;
            ff0 = this.F_A;
         }
         if(this.fi == 0 && this.Fi_vx != 0)
         {
            if(Math.abs(this.Fi_vx) <= FF0)
            {
               this.Fi_vx = 0;
               this.ff = 0;
            }
            else
            {
               this.ff = -Maths.Pn(this.Fi_vx) * ff0;
            }
         }
         else
         {
            this.ff = 0;
         }
         ax = this.fi + this.ff;
         ay = this.fg;
         if(this.Fi_vy > 0)
         {
            ay = FG0 * this.dropSpeedMul;
         }
         this.Fi_vx += ax;
         this.Fi_vy += ay;
         var fi_vmax0:Number = (this.Fi_vxmax * this.maxStateMul * this.out_maxStateMul + this.maxStateValue) * this.allMaxStateMul;
         if(this.jumpMustVxMax != 0)
         {
            if(!this.isGroundB())
            {
               fi_vmax0 = this.jumpMustVxMax;
            }
         }
         if(this.Fi_vx > fi_vmax0)
         {
            this.Fi_vx = fi_vmax0;
         }
         else if(this.Fi_vx < -fi_vmax0)
         {
            this.Fi_vx = -fi_vmax0;
         }
         if(this.dof.left == 1)
         {
            if(this.Fi_vx < 0)
            {
               this.Fi_vx = 0;
            }
            if(this.e_vx < 0)
            {
               this.e_vx = 0;
            }
            if(ax < 0)
            {
               ax = 0;
            }
            if(this.dof.left_back >= 2)
            {
               x += this.dof.left_back;
            }
         }
         if(this.dof.right == 1)
         {
            if(this.Fi_vx > 0)
            {
               this.Fi_vx = 0;
            }
            if(this.e_vx > 0)
            {
               this.e_vx = 0;
            }
            if(ax > 0)
            {
               ax = 0;
            }
            if(this.dof.right_back >= 2)
            {
               x -= this.dof.right_back;
            }
         }
         if(this.dof.up == 1)
         {
            if(this.Fi_vy < 0)
            {
               this.Fi_vy = 0;
            }
            if(this.e_vy < 0)
            {
               this.e_vy = 0;
            }
            if(ay < 0)
            {
               ay = 0;
            }
            if(this.dof.up_back >= 2)
            {
               y += this.dof.up_back;
            }
         }
         if(this.dof.down == 1)
         {
            if(Math.abs(this.e_vx) < FF0)
            {
               this.e_vx = 0;
            }
            else
            {
               this.e_vx += -Maths.Pn(this.e_vx) * FF0;
            }
            this.nowJumpNum = 0;
            this.nowSprintNum = 0;
            if(this.e_vy > 0)
            {
               this.e_vy = 0;
            }
            if(this.dof.hitType == DofHitType.slope && Math.abs(this.dof.slopeAngle) < Math.PI / 5)
            {
               e_ra = this.dof.slopeAngle;
               e_vy0 = this.Fi_vx * Math.tan(e_ra);
               if(e_vy0 < 0)
               {
                  if(this.Fi_vy > e_vy0)
                  {
                     this.Fi_vy = e_vy0;
                     this.isSlopeVyB = true;
                     this.slope_vy = e_vy0;
                  }
               }
               else
               {
                  this.Fi_vy = e_vy0;
                  this.isSlopeVyB = false;
                  this.slope_vy = e_vy0;
               }
               if(this.dof.down_back >= 3)
               {
                  y -= this.dof.down_back;
               }
            }
            else
            {
               if(this.Fi_vy > 0)
               {
                  this.Fi_vy = 0;
               }
               if(this.dof.down_back >= 2)
               {
                  y -= this.dof.down_back;
               }
            }
            if(ay > 0)
            {
               ay = 0;
            }
         }
         if(this.Fi_vy > this.Fi_vymax)
         {
            this.Fi_vy = this.Fi_vymax;
         }
         else if(this.Fi_vy < -this.Fi_vymax)
         {
            this.Fi_vy = -this.Fi_vymax;
         }
         vx = this.Fi_vx + this.e_vx + this.state_e_vx;
         vy = this.Fi_vy + this.e_vy + this.state_e_vx;
         if(vx > vxmax)
         {
            vx = vxmax;
         }
         else if(vx < -vxmax)
         {
            vx = -vxmax;
         }
         if(vy > vymax)
         {
            vy = vymax;
         }
         else if(vy < -vymax)
         {
            vy = -vymax;
         }
         x += vx * MainMotion.SPEED_SCALE;
         y += vy * MainMotion.SPEED_SCALE;
      }
      
      private function fallPan() : void
      {
         var bb0:Boolean = this.dof.down == 0;
         if(bb0 != this.nowIsAirB)
         {
            this.nowIsAirB = bb0;
            if(!bb0)
            {
               if(this.nowFallFirstY != -10000)
               {
                  if(y - this.nowFallFirstY > this.maxFallHigh)
                  {
                     this.maxFallHigh = y - this.nowFallFirstY;
                  }
               }
            }
         }
         if(!bb0)
         {
            this.nowFallFirstY = y;
         }
         var maxFly0:int = -(y - this.nowFallFirstY);
         if(maxFly0 > this.maxFlyHigh)
         {
            this.maxFlyHigh = maxFly0;
         }
      }
      
      public function startTimer() : void
      {
         beforeX = x;
         beforeY = y;
      }
      
      public function motionTimer() : void
      {
         if(enabled)
         {
            if(this.motionEnabled && !this.outOfWorldB)
            {
               if(this.state == GroundMotionState.stand)
               {
                  this.baseCount();
                  if(this.delayT != -100)
                  {
                     this.delayHandler();
                  }
                  if(this.countFlyB)
                  {
                     this.fallPan();
                  }
               }
               else if(this.state == GroundMotionState.fly)
               {
                  this.flyCount();
               }
               if(this.raBySlopeB)
               {
                  this.raSlopeCount();
               }
               else if(this._def.motionD.imgRaB)
               {
                  if(vx != 0 && vy != 0)
                  {
                     this.inputRa(-Math.atan2(vy,vx));
                  }
               }
            }
            this.hitRect.x = this.HIT_RECT.x + x;
            this.hitRect.y = this.HIT_RECT.y + y;
            this.hitRect.width = this.HIT_RECT.width;
            this.hitRect.height = this.HIT_RECT.height;
            this.MX = this.hitRect.x + this.hitRect.width / 2;
            this.MY = this.hitRect.y + this.hitRect.height / 2;
            this.hitRect.flesh();
         }
      }
   }
}

