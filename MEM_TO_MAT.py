#Startup Code Begin
import param
import model
import Transform3D
#Startup Code End

def mem_to_mtrl(m1,m2):
    mt = m1.Material[0]
    if mt.main_mtrl==True:
        pass
    else:
        param.Warning("Index 0 material not main material for this member!!!")
        return
    t = mt._as_tuple
    xform = Transform3D.Transform3D(t[0],t[2])
    new_mt = model.CopyMaterialToMember(mt,m2,xform)
    model.EraseMember(m1.number)
    return

def main():
    if model.LocateMultiple('Select Members to Make Material',model.IsMember):
        mlist = model.GetSelection()
        param.ClearSelection()
    else:
        param.Warning("No Selection Made!!!")
        return

    if model.LocateSingle("Select member to move to:",model.IsMember):
        m2 = model.selected_member()
        param.ClearSelection()
    else:
        param.Warning("This is not a valid member!!!")

    if len(mlist)==0:
        param.Warning("No Selection Made!!!")
        return
    else:
        for m in mlist:
            mem_to_mtrl(m,m2)

    return

if __name__=='__main__':
    main()
