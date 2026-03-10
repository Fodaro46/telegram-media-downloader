package esame21_06_23;

public abstract class PavimentoAstratto {
    int lunghezza;
    int altezza ;

    int[][] pavimento;
    public PavimentoAstratto(int lunghezza, int altezza){
        this.lunghezza=lunghezza;
        this.altezza=altezza;
        for(int i=0;i<lunghezza;i++)
            for(int j=0;j<altezza;j++)
                pavimento[i][j]=-1;

    }

    public abstract String inizia(int T) throws InterruptedException;
    public abstract void finisci(int T, String B) throws InterruptedException;
}
