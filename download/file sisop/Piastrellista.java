package esame21_06_23;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class Piastrellista extends Thread{
    PavimentoAstratto p;
    int Tipo;
    public Piastrellista (PavimentoAstratto p,int Tipo){
        this.p=p;
        this.Tipo=Tipo;
    }

    public void run(){
        try{
            String x="";
            while(true) {
                TimeUnit.MINUTES.sleep(1);
                x=p.inizia(this.Tipo);
                if(x==null)
                    return;
                if (this.Tipo == 0)
                    TimeUnit.MINUTES.sleep(lavora(6, 5));
                else
                    TimeUnit.MINUTES.sleep(lavora(3, 2));
                p.finisci(this.Tipo, x);
                System.out.println("il piastrellista ha terminato il suo lavoro ora si riposa");
                TimeUnit.MINUTES.sleep(1);
            }

        }catch(InterruptedException e){
        }
    }

    private int lavora(int max, int min){
        return new Random().nextInt(max-min+1);
    }

}
