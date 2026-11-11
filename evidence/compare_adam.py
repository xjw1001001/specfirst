import sys, math
import pyarrow.parquet as pq
import pyarrow as pa
from pathlib import Path
adam=Path(sys.argv[1]); names=sys.argv[2:]
ALIAS={"adqsnipx":"adqsnpix"}
tot_cells=tot_bad=0
for ds in names:
    exp=pq.read_table(adam/f"{ALIAS.get(ds,ds)}.parquet"); got=pq.read_table(adam/f"{ds}-yamaa.parquet")
    msg=[]
    if exp.num_rows!=got.num_rows: msg.append(f"rows exp={exp.num_rows} got={got.num_rows}")
    if exp.schema.names!=got.schema.names: msg.append(f"columns differ: missing={sorted(set(exp.schema.names)-set(got.schema.names))} extra={sorted(set(got.schema.names)-set(exp.schema.names))}")
    bad=0; cells=exp.num_rows*exp.num_columns; badcols=[]
    if exp.num_rows==got.num_rows:
        for c in exp.schema.names:
            if c not in got.schema.names: bad+=exp.num_rows; badcols.append(c+':missing'); continue
            a=exp.column(c).to_pylist(); b=got.column(c).to_pylist(); nb=0
            for x,y in zip(a,b):
                if x is None or y is None:
                    if x is not y: nb+=1
                elif isinstance(x,(int,float)) and isinstance(y,(int,float)) and not isinstance(x,bool):
                    if isinstance(x,float) and math.isnan(x) and isinstance(y,float) and math.isnan(y): continue
                    if abs(x-y)>1e-10: nb+=1
                elif x!=y: nb+=1
            if nb: badcols.append(f"{c}:{nb}")
            bad+=nb
        typ=[c for c in exp.schema.names if c in got.schema.names and exp.schema.field(c).type!=got.schema.field(c).type]
    else:
        bad=cells; typ=[]
    tot_cells+=cells; tot_bad+=bad
    print(f"{ds.upper():9s} rows={exp.num_rows:6d} cols={exp.num_columns:3d} cells={cells:8d} mismatched={bad:6d} type_diffs={len(typ)} {'; '.join(msg)} {' '.join(badcols[:8])}")
print(f"TOTAL cells={tot_cells} mismatched={tot_bad} match={(1-tot_bad/tot_cells)*100:.4f}%")
