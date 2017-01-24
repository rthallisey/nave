for i in $(seq 1 $1); do
  for j in $(ls *template.yaml); do
    f=$(echo $j | sed -e s,template,$i,)
    cp $j $f
    sed -i "s,{{count}},$i,g" $f
    #oc/kubectl create $f ?
  done
done
