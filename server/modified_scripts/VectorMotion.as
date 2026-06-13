package com.sounto.motion
{
   import com.sounto.math.Maths;
   
   public class VectorMotion extends MainMotion
   {
      
      public var mx:Number = 0;
      
      public var my:Number = 0;
      
      public var v:Number = 0;
      
      public var vmax:Number = 100;
      
      public var vmin:Number = 0;
      
      public var a:Number = 0;
      
      public var ra:Number = 0;
      
      public var vra:Number = 0;
      
      public var ara:Number = 0;
      
      public var selfVra:Number = 0;
      
      public var selfRa:Number = 0;
      
      public var vraMax:Number = 0.16666666666666666;
      
      public var followVra:Number = 0;
      
      public var F_G:Number = 1;
      
      public var fg:Number = 0;
      
      public var gravity:Number = 0;
      
      public var followWay:String = "missile";
      
      public var followB:Boolean = false;
      
      public var followEachB:Boolean = true;
      
      public function VectorMotion()
      {
         super();
      }
      
      public function setInit(x00:Number, y00:Number, v00:Number, ra0:Number, _vmax:Number = 100, _va:Number = 0, _vmin:Number = 0) : void
      {
         x = x00;
         y = y00;
         this.v = v00;
         this.ra = ra0;
         this.vmax = _vmax;
         this.vmin = _vmin;
         this.a = _va / INIT.FPS;
         this.count(false);
      }
      
      public function stopAll() : void
      {
         this.gravity = 0;
         vx = 0;
         vy = 0;
         this.v = 0;
         this.a = 0;
         this.vra = 0;
         this.ara = 0;
         this.selfVra = 0;
      }
      
      public function startFollow(mx0:Number, my0:Number) : void
      {
         this.mx = mx0;
         this.my = my0;
         this.followB = true;
      }
      
      public function stopFollow() : void
      {
         this.followB = false;
         this.vra = 0;
      }
      
      public function getGapByM() : Number
      {
         return Maths.Long(this.mx - x,this.my - y);
      }
      
      public function addV(vx0:Number, vy0:Number, mulB:Boolean = false) : void
      {
         if(mulB)
         {
            vx *= vx0;
            vy *= vy0;
         }
         else
         {
            vx += vx0;
            vy += vy0;
         }
         this.fleshByVxVy();
      }
      
      public function addV_byRa(ra0:Number, mul0:Number) : void
      {
         var vx0:Number = this.v * mul0 * Math.cos(ra0);
         var vy0:Number = this.v * mul0 * Math.sin(ra0);
         this.addV(vx0,vy0);
      }
      
      public function forceByRa(ra0:Number, vra0:Number) : void
      {
         var cra0:Number = Maths.J_J(this.ra,ra0);
         if(cra0 > vra0)
         {
            this.vra = (Maths.LineVsJ(this.ra,ra0) < 0 ? 1 : -1) * vra0;
         }
      }
      
      public function setV(vx0:Number, vy0:Number) : void
      {
         vx = vx0;
         vy = vy0;
         this.fleshByVxVy();
      }
      
      protected function count(addDataB0:Boolean = true) : void
      {
         this.fg = this.F_G * this.gravity;
         if(addDataB0)
         {
            this.vra += this.ara;
            this.ra += this.vra;
            if(this.a != 0)
            {
               this.v += this.a;
            }
         }
         if(this.selfRa >= Math.PI * 10)
         {
            this.selfRa = 0;
         }
         else
         {
            this.selfRa += this.selfVra;
         }
         if(this.v > this.vmax)
         {
            this.v = this.vmax;
         }
         else if(this.v < -this.vmax)
         {
            this.v = -this.vmax;
         }
         if(this.v >= 0 && this.v < this.vmin)
         {
            this.v = this.vmin;
         }
         if(this.v < 0 && this.v > -this.vmin)
         {
            this.v = -this.vmin;
         }
         vx = Math.cos(this.ra) * this.v;
         vy = Math.sin(this.ra) * this.v + this.fg;
         this.fleshByVxVy();
         if(addDataB0)
         {
            x += vx * MainMotion.SPEED_SCALE;
            y += vy * MainMotion.SPEED_SCALE;
         }
      }
      
      private function fleshByVxVy() : void
      {
         this.v = Maths.Long(vx,vy);
         if(vx != 0 || vy != 0)
         {
            this.ra = Math.atan2(vy,vx);
         }
      }
      
      protected function followCount() : void
      {
         var cs:Number = NaN;
         var tra:Number = Math.atan2(this.my - y,this.mx - x);
         var cra:Number = tra - this.ra;
         if(this.followWay == MotionFollowWay.missile)
         {
            cs = Maths.Long(this.mx - x,this.my - y);
            if(cs < 200)
            {
               this.vra = Math.sin(cra) * this.vraMax * this.followVra * (250 - cs) / 50;
            }
            else
            {
               this.vra = Math.sin(cra) * this.vraMax * this.followVra;
            }
         }
         else if(this.followWay == MotionFollowWay.normal)
         {
            this.vra = Math.sin(cra) * this.vraMax * this.followVra;
         }
      }
      
      public function motionTimer() : void
      {
         if(enabled)
         {
            if(this.followB && this.followEachB)
            {
               this.followCount();
            }
            this.followEachB = true;
            this.count();
         }
      }
   }
}

