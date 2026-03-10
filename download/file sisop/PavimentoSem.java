package esame21_06_23;

import java.util.concurrent.Semaphore;

public class PavimentoSem extends PavimentoAstratto{
    Semaphore mutex=new Semaphore(1);
    Semaphore[] S=new Semaphore[] {new Semaphore (lunghezza), new Semaphore(0 )};

    public PavimentoSem(int lunghezza, int altezza) {
        super(lunghezza, altezza);

    }

    @Override
    public String inizia(int T) throws InterruptedException{
        S[T].acquire();
        mutex.acquire();
        String blocco = ricercaEAssegnaBlocco(T);
        mutex.release();
        return blocco;
    }

    private String ricercaEAssegnaBlocco(int T) {
        for (int i =0;i<lunghezza; i++){
            for(int j=0;j< altezza; j++){
                if(T==0){
                    if(i==0){
                        if(pavimento[i][j]== -1){
                            pavimento[i][j]=0;
                            return "B_"+i+"_"+j;
                        }
                    }
                    else{
                        if(pavimento[i][j]== -1 && pavimento[i-1][j]==2) {
                            pavimento[i][j] = 0;
                            return "B_" + i + "_" + j;
                        }
                    }
                }
                else{
                    if(pavimento[i][j]== 1){
                        pavimento[i][j] = 0;
                        return "B_" + i + "_" + j;
                    }
                }
            }
        }
        return null;
    }

    @Override
    public void finisci(int T, String B) throws InterruptedException{
        mutex.acquire();
        for(int i=0;i<lunghezza;i++) {
            for (int j = 0; j < altezza; j++) {
                if (T == 0) {
                    pavimento[i][j] = 1;
                } else
                    pavimento[i][j] = 2;
                S[1 - T].release();
                mutex.release();
            }
        }
    }
}
