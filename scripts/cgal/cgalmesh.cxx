#include <fstream>
#include <CGAL/Surface_mesh_default_triangulation_3.h>
#include <CGAL/Complex_2_in_triangulation_3.h>
#include <CGAL/make_surface_mesh.h>
#include <CGAL/Implicit_surface_3.h>
#include <CGAL/IO/Complex_2_in_triangulation_3_file_writer.h>

typedef CGAL::Surface_mesh_default_triangulation_3 Tr;
typedef CGAL::Complex_2_in_triangulation_3<Tr> C2t3;
typedef Tr::Geom_traits GT;
typedef GT::Sphere_3 Sphere_3;
typedef GT::Point_3 Point_3;
typedef GT::FT FT;
typedef FT (*Function)(Point_3);
typedef CGAL::Implicit_surface_3<GT, Function> Surface_3;

FT surface_function(Point_3 p)
{
    const FT x = p.x(), y = p.y(), z = p.z();
    return z - 0.555*sin(M_PI * x) * cos(M_PI * y);
}

int main()
{
    Tr tr;         // 3D-Delaunay triangulation
    C2t3 c2t3(tr); // 2D-complex in 3D-Delaunay triangulation
    // defining the surface
    Surface_3 surface(surface_function,            // pointer to function
                      Sphere_3(CGAL::ORIGIN, 2.)); // bounding sphere
    // Note that "2." above is the *squared* radius of the bounding sphere!
    // defining meshing criteria
    CGAL::Surface_mesh_default_criteria_3<Tr> criteria(30.,  // angular bound
                                                       0.1,  // radius bound
                                                       0.1); // distance bound
    // meshing surface
    CGAL::make_surface_mesh(c2t3, surface, criteria, CGAL::Non_manifold_tag());
    std::cout << "Final number of points: " << tr.number_of_vertices() << "\n";
    std::ofstream out("out.off");
    CGAL::output_surface_facets_to_off(out, c2t3);
}