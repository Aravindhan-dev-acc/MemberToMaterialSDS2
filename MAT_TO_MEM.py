'''
Creates a Member out of Existing Material

Author: Kyle Martin
Company: Martech Solutions LLC

This script is still under development and is being shared as-is. Author
reserves no responsibility for errors that may occur due to usage.
'''

# Startup Code Begin
import param
import model
import member
import Transform3D
import Point3D
from point import Point


# Startup Code End

def get_xform(mt):
    t = mt._as_tuple
    x = Transform3D.Transform3D(t[0], t[2])
    return x


def mtrl_to_gen_mtrl(mt):
    t = mt._as_tuple
    m = member.Member(t[0]).material(t[2])
    return m


def add_angle(mt):
    xform = mt.ref_xform
    pt1 = Point3D.Point3D(xform[-1][:3])
    pt2 = pt1 + Point3D.Point3D(xform[0]) * mt.length
    d = pt1.distance(pt2)

    m = member.Member('Misc Rolled Section')
    m.LeftEnd.Location = Point(pt1)
    m.RightEnd.Location = Point(pt2)
    m.SectionSize = mt.description
    m.MaterialGrade = 'A36'
    m.WorkpointSlopeDistance = d
    m.ToeInOrOut = mt.toe_io

    m.Add()
    mnumber = m.number

    return mnumber


def add_rect_plate(mt):
    xform = mt.ref_xform
    pt1 = Point3D.Point3D(xform[-1][:3])
    pt2 = pt1 + Point3D.Point3D(xform[0]) * mt.length
    d = pt1.distance(pt2)

    m = member.Member('Misc Rectangular Plate')
    m.LeftEnd.Location = Point(pt1)
    m.RightEnd.Location = Point(pt2)
    m.WorkpointSlopeDistance = d
    # m.Width = mt.width
    # m.Thickness = 1

    m.Add()

    # m.Thickness = 0
    # m.Thickness =mt.thick
    mnumber = m.number
    print(mnumber)
    return mnumber


def add_bnt_plate(mt):
    xform = mt.ref_xform
    pt1 = Point3D.Point3D(xform[-1][:3])
    pt2 = pt1 + Point3D.Point3D(xform[0]) * mt.length
    d = pt1.distance(pt2)

    m = member.Member('Misc Bent Plate')
    m.LeftEnd.Location = Point(pt1)
    m.RightEnd.Location = Point(pt2)
    m.WorkpointSlopeDistance = d
    m.IncludedAngle = mt.bend_angle
    m.BentPlateLeg = mt.leg
    m.BentPlateOSL = mt.osl
    m.Thickness = mt.thick

    m.Add()
    mnumber = m.number

    return mnumber

def round_bar(mt):
    xform = mt.ref_xform
    # print(xform)
    # pt1 = Point3D.Point3D(xform[-1][:3])
    # pt2 = pt1 + Point3D.Point3D(xform[0]) * mt.length
    # d = pt1.distance(pt2)
    #
    # m = member.Member('Misc Bent Plate')
    # m.LeftEnd.Location = Point(pt1)
    # m.RightEnd.Location = Point(pt2)
    # m.WorkpointSlopeDistance = d
    # m.IncludedAngle = mt.bend_angle
    # m.BentPlateLeg = mt.leg
    # m.BentPlateOSL = mt.osl
    # m.Thickness = mt.thick
    #
    # m.Add()
    # mnumber = m.number
    #
    # return mnumber
    layout = Layout3D()

    ptList = xform

    for pt, r in ptList:
        layout.add_node(Point3D(pt), r)
    layout.set_depth_vectors(Point3D(plane.N), False)
    rb1 = member.Member('Misc Round Bar')
    # rb1.Member = mem
    # rb1.MaterialGrade = "A36"
    rb1.Centered = "Yes"
    rb1.BarDiameter = linkDia
    rb1.MaterialType = "Round bar"
    rb1.SurfaceFinish = "None"
    rb1.MaterialColor3d = validColTup("255,0,0")
    rb1.mtrl_usage = "Link Chain"
    rb1.description = 'LINK CHAIN-%s' % (dim_print(linkDia))
    rb1.ReferencePointOffset = (0, 0, 0)
    rb1.mtrl_is_main = "No"
    rb1.dummy = "Yes"
    rb1.layout = layout
    # try:
    rb1.Add()
    mnumber = rb1.number

    return mnumber

def mtrl_to_mem(mt):
    xform = get_xform(mt)
    mt_type = mt.mtrl_type.value
    if mt_type == 'Angle':
        mem_number = add_angle(mt)
    elif mt_type == 'PlateMaterial':  # Rectangular Plate
        mem_number = add_rect_plate(mt)
    elif mt_type == 'BentPlate':
        mem_number = add_bnt_plate(mt)
    elif mt_type == 'RoundBar':
        mem_number = round_bar(mt)
    else:
        param.Warning("Not a Valid Material Type or Not Covered by This Program :(")

    # Copy Material to New Member
    m = model.member(mem_number)
    new_mtrl = model.CopyMaterialToMember(mt, m, xform)
    mem = member.Member(mem_number).MainMaterial().Erase()

    # #Delete Material from Previous Member
    # t = mt._as_tuple
    # m_past = member.Member(t[0])
    # m_past.material(t[2]).erase() #Consider deleting by guid for multi-user environment???

    # Set new_mtrl as Member Main Material
    model.ChangeOneMaterial(new_mtrl,
                            [('main_mtrl', True)])  # Consider using model.LockOnlyThis and model.Unlock if shared model

    return mt


def main():
    if model.LocateMultiple("Select Material(s)", model.IsMaterial):
        mt = model.GetSelection()
        param.ClearSelection()

        if len(mt) == 0:
            param.Warning("No Material Selected")
            return
        else:
            old_mtrl = []
            for x in mt:
                old = mtrl_to_mem(x)
                t = x._as_tuple
                mem = t[0]
                g = mtrl_to_gen_mtrl(x).guid
                old_mtrl.append((mem, g))

            temp = {x: [] for x in set([y[0] for y in old_mtrl])}
            for x in old_mtrl:
                k = x[0]
                v = x[1]
                temp[k].append(v)

            for k in temp.keys():
                m = member.Member(k)
                n_mtrl = len(temp[k])  # number of materials in need of deletion
                for i in range(n_mtrl):
                    for j in range(m.mtrl_quantity):
                        if m.material(j).guid == temp[k][i]:
                            m.material(j).erase()
                            break
                        else:
                            pass
            return

    else:
        param.Warning("No Selection Made")
        return


if __name__ == '__main__':
    main()